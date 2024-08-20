import json
import boto3
import urllib3

def lambda_handler(event, context):
    try:
  
        session_data = get_sessionize_data()
        processed_data = process_session_data(session_data)
        
        result = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup'),
                'apiPath': event.get('apiPath'),
                'httpMethod': event.get('httpMethod'),
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': processed_data,
                    },
                },
                'sessionAttributes': {},
                'promptSessionAttributes': {},
            },
            }

        print(result)
        return result
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_sessionize_data():
    sessionize_url = 'https://sessionize.com/api/v2/9nu3ymhm/view/Sessions'
    
    http = urllib3.PoolManager()
    response = http.request('GET', sessionize_url)
    
    if response.status == 200:
        return json.loads(response.data.decode('utf-8'))
    else:
        raise Exception(f"Failed to retrieve data: {response.status}")

def process_session_data(session_data):
    
    sessions = []
    for session_group in session_data:
        for session in session_group['sessions']:
            sessions.append({
                "title": session.get('title'),
                "description": session.get('description', ''),
                "speakers": [speaker['name'] for speaker in session.get('speakers', [])],
                "startsAt": session.get('startsAt'),
                "endsAt": session.get('endsAt'),
                "room": session.get('room')
            })
    return sessions
    