import json
import boto3
from boto3.dynamodb.conditions import Key
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('faqs_table'))

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))

    parameters = event.get('parameters')
    api_path = event.get('apiPath')
    id_event = next((param['value'] for param in parameters if param['name'] == 'id_event'), None)
    print(id_event)
    response = {}

    if api_path == '/faqs':
        events_info = get_faqs(id_event)
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

def get_faqs(id_event):
    if not id_event:
        return { 'error': 'IdEvent is required.' }

    try:
        response = table.scan(
            FilterExpression=Key('id_event').eq(id_event)
        )

        if 'Items' in response and response['Items']:
            print(response['Items'])
            items += response['Items']
            return items
        else:
            return {'error': 'Info not found'}

    except Exception as e:
        print(e)
        return {'error': str(e)}
