import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_name = 'readings'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        response = table.scan(FilterExpression=Key('SensorID').eq('humidity'))
        items = response['Items']
        readings = [float(item['Reading']) for item in items]
        avg_reading = sum(readings) / len(readings)
        return {
            'statusCode': 200,
            'body': json.dumps({'average_humidity': avg_reading})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
