import boto3
import json
from botocore.exceptions import ClientError
import decimal
from boto3.dynamodb.conditions import Attr

tableName = "readings"
dynamo = boto3.resource('dynamodb').Table(tableName)

# Necessary due to error that was encountered where json couldn't encode decimals in data
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    try:
        sensor_ids = event['multiValueQueryStringParameters'].get('sensor_id', [])
        metrics = event['multiValueQueryStringParameters'].get('metrics', [])
        stat = event['queryStringParameters'].get('statistic')
        start_date = event['queryStringParameters'].get('start_date')
        end_date = event['queryStringParameters'].get('end_date')

        # Build filter expression
        filter_expr = Attr('sensor_id').is_in(sensor_ids)
        if start_date:
            filter_expr = filter_expr & Attr('timestamp').gte(start_date)
        if end_date:
            filter_expr = filter_expr & Attr('timestamp').lte(end_date)

        response = dynamo.scan(FilterExpression=filter_expr)

        items = response['Items']
        if metrics:
            new_items = []
            for metric in metrics:
                values = [item[metric] for item in items if metric in item and item['sensor_id'] in sensor_ids]
                if values:
                    if stat == 'max':
                        max_value = max(values)
                        new_items.append({'metric': metric, 'statistic': 'max', 'value': max_value})
                    elif stat == 'min':
                        min_value = min(values)
                        new_items.append({'metric': metric, 'statistic': 'min', 'value': min_value})
                    elif stat == 'sum':
                        sum_value = sum(values)
                        new_items.append({'metric': metric, 'statistic': 'sum', 'value': sum_value})
                    elif stat == 'average':
                        avg_value = sum(values) / len(values)
                        new_items.append({'metric': metric, 'statistic': 'average', 'value': avg_value})
                    else:
                        return {
                            'statusCode': 400,
                            'body': json.dumps('Invalid stat parameter')
                        }

            # Remove the original items that are not part of the requested metrics
            items = [item for item in items if 'metric' in item or item['sensor_id'] in sensor_ids]
            
            # Merge the new items with the original items
            items += new_items

        return {
            'statusCode': 200,
            'body': json.dumps(items, cls=DecimalEncoder, indent=2)
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error reading from DynamoDB table: ' + str(e))
        }
