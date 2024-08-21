import json
import boto3
from boto3.dynamodb.conditions import Key
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('events_table'))

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))

    api_path = event.get('apiPath')
    response = {}

    if api_path == '/event':
        events_info = get_events_info()
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

def get_events_info():
    try:
        response = table.scan(
            FilterExpression=Key('status').eq("1")
        )
        items=[]
        if 'Items' in response and response['Items']:
            print(response['Items'])
            items += response['Items']
            return items
        else:
            return {'error': 'Info not found'}
        
    except Exception as e:
        print(e)
        return {'error': str(e)}