import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
import string

tableName = "readings"
dynamo = boto3.resource('dynamodb').Table(tableName)

def lambda_handler(event, context):
    try:
        item = {
            'timestamp': str(datetime.now()),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sensor_id': event['sensor_id'],
            'temperature': event['temperature'],
            'humidity': event['humidity'],
            'wind_speed': event['wind_speed'],
        }
        dynamo.put_item(Item=item, ConditionExpression='attribute_not_exists(sensor_id)')
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully inserted item into DynamoDB table')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error writing to DynamoDB table: ' + str(e))
        }