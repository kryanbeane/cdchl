import boto3
import json
from botocore.exceptions import ClientError
import decimal

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
        response = dynamo.scan()
        items = response['Items']
        return {
            'statusCode': 200,
            'body': json.dumps(items, cls=DecimalEncoder)
  }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error reading from DynamoDB table: ' + str(e))
        }
