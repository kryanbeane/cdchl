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
            'Timestamp': str(datetime.now()),
            'SensorID': event['SensorID'],
            'Temperature': event['Temperature'],
            'Humidity': event['Humidity'],
            'Wind Speed': event['Wind Speed'],
        }
        dynamo.put_item(Item=item, ConditionExpression='attribute_not_exists(SensorID)')
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully inserted item into DynamoDB table')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error writing to DynamoDB table: ' + str(e))
        }