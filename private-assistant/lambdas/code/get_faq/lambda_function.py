import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('faqs_table')

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))

    api_path = event.get('apiPath')
    country_event = event.get('CountryEvent')
    question = event.get('Question')
    response = {}

    if api_path == '/faqs':
        events_info = get_faq(country_event, question)
        print(events_info)
        response = events_info

    result = {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup'),
            'apiPath': event.get('apiPath'),
            'httpMethod': event.get('httpMethod'),
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': response,
                },
            },
            'sessionAttributes': {},
            'promptSessionAttributes': {},
        },
    }

    print(result)
    return result

def get_faq(country_event, question):
    if not country_event or not question:
        return {
            "statusCode": 400,
            "body": "CountryEvent y Question are required."
        }

    try:
        response = table.get_item(
            Key={
                'CountryEvent': country_event,
                'Question': question
            }
        )

        if 'Item' in response:
            return response['Item']['Answer']
        else:
            return "Question not found."

    except ClientError as e:
        return f"Error  DynamoDB: {str(e)}"
