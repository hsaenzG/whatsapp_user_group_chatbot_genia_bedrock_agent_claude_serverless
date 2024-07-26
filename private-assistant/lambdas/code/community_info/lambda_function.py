import json
import boto3
from boto3.dynamodb.conditions import Key
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('community_table'))

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))

    api_path = event.get('apiPath')
    response = {}

    if api_path == '/community':
        events_info = get_community_info()
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

def get_community_info():
    try:
        response = table.scan(
            FilterExpression=Key('status').eq(1)
        )
        if 'Items' in response and response['Items']:
            return response['Items'][0]
        else:
            return {'error': 'Info not found'}
    except Exception as e:
        print(e)
        return {'error': str(e)}
