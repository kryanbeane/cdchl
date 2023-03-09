import boto3
import json
from botocore.exceptions import ClientError
import decimal
import numpy as np
from boto3.dynamodb.conditions import Attr
from datetime import datetime
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
        timestamp_str = event['queryStringParameters'].get('timestamp')
        if timestamp_str:
            # Convert timestamp_str to a string
            response = dynamo.get_item(
                Key={
                    'timestamp': timestamp_str
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'], cls=DecimalEncoder)
            }
        
        sensor_filtered_items = filter(event)

        return {
            'statusCode': 200,
            'body': json.dumps(sensor_filtered_items, cls=DecimalEncoder)
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error reading from DynamoDB table: ' + str(e))
        }
        
def filter(event):
    metrics_str = event['queryStringParameters'].get('metrics')
    statistic_str = event['queryStringParameters'].get('statistic', 'mean')
    start_date_str = event['queryStringParameters'].get('start_date')
    end_date_str = event['queryStringParameters'].get('end_date')
    
    items = filter_by_sensor(event)
        
    if not metrics_str:
        return items
    
    if start_date_str and end_date_str:
        items = filter_by_date_range(items, start_date_str, end_date_str)
        
    # Compute requested statistics for each metric
    metrics = metrics_str.split(',') if metrics_str else []
    metric_stats = {}
    for metric in metrics:
        metric_values = [item[metric] for item in items if metric in item]
        if statistic_str == 'min':
            metric_stats[metric] = np.min(metric_values)
        elif statistic_str == 'max':
            metric_stats[metric] = np.max(metric_values)
        elif statistic_str == 'sum':
            metric_stats[metric] = np.sum(metric_values)
        else:
            metric_stats[metric] = np.mean(metric_values)

    # Return requested statistics and reading timestamps
    response_items = []
    for metric, stat in metric_stats.items():
        response_items.append(f"{metric} {statistic_str}: {stat}")
        
    response_items.extend([f"Weather Reading timestamp {item['timestamp']}" for item in items])
    return response_items


def filter_by_date_range(items, start_date_str, end_date_str):
    if start_date_str and end_date_str:
        start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        items = [item for item in items if start <= datetime.strptime(item['date'], '%Y-%m-%d').date() <= end]
    return items

def filter_by_sensor(event):
    try:
        sensor_ids_str = event['queryStringParameters'].get('sensor_ids')

        if sensor_ids_str:
            
            # Convert sensor_ids_str to a list of integers
            sensor_ids = [int(id) for id in sensor_ids_str.split(',') if id.isdigit()]

            # Query for items matching the specified sensor_ids
            response = dynamo.scan(
                FilterExpression=Attr('sensor_id').is_in(sensor_ids)
            )
            
            return response['Items']
        else:
            return dynamo.scan()['Items']
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error enountered while filtering by Sensor: ' + str(e))
        }
