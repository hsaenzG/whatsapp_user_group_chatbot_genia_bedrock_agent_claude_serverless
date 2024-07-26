#####################################################
## This function queries anthropic.claude-3-sonnet ##
#####################################################

import json
import boto3
import os
import time
import base64
import sys
import requests

from db_utils import (update_items_out,save_item_ddb,query,update_item_session)

from utils import whats_reply

BucketName = os.environ.get('BucketName')
ImageKeyName = os.environ.get('ImageKeyName')
model_id = os.environ.get('ENV_MODEL_ID_V3')
accept = 'application/json'
contentType = 'application/json'
anthropic_version = os.environ.get('ENV_ANTHROPIC_VERSION')

agentId=os.environ.get('agentId')
agentAlias = os.environ.get('agentAliasId').split('|')
agentAliasId=agentAlias[1]

whatsapp_out_lambda = os.environ.get('WHATSAPP_OUT')
table_name_active_connections = os.environ.get('whatsapp_MetaData')

client_s3 = boto3.client('s3')
dynamodb_resource=boto3.resource('dynamodb')
bedrock_client = boto3.client("bedrock-runtime")
table_name_session = os.environ.get('session_table_history')

base_path="/tmp/"
table = dynamodb_resource.Table(table_name_active_connections)
table_session_active = dynamodb_resource.Table(os.environ['user_sesion_metadata'])


def add_text(role, content, history):
    print("expand history items into new_history")
    # expand history items into new_history
    new_history = [h for h in history]
    new_history.append({"role":role,"content":content})
    return new_history

def save_history(table,item):
    print("put item")
    dynamodb_resource=boto3.resource('dynamodb')
    table_session_active = dynamodb_resource.Table(table)
    response = table_session_active.put_item(Item=item)
    print(response)
    return True
    
def load_history(table, sessionid):
    response = table.get_item(Key={"id": sessionid})
    return response.get("Item")
    
def query_history(key,table,keyvalue):
    print("Query History")
    dynamodb_resource=boto3.resource('dynamodb')
    table_session_active = dynamodb_resource.Table(table)
    response = table_session_active.query(
        KeyConditionExpression=Key(key).eq(keyvalue)
    )
    print(response)
    return response['Items'][0]

def agent_text(model_id, anthropic_version, text, max_tokens,history):
    system_prompt = """The following is a friendly conversation between a human and an AI. 
    The AI is talkative and provides lots of specific details from its context. 
    If the AI does not know the answer to a question, it truthfully says it does not know.
    Always reply in the original user language.
    """
    boto3_bedrock = boto3.client("bedrock-runtime")
    content = [{"type":"text","text":text}]
    new_history = add_text("user",content, history)
    #text  = '\n'.join([f"<document>{doc.page_content}</document>" for doc in docs])
    body = {
        "system": system_prompt,
        "messages":new_history,"anthropic_version":anthropic_version,
        "max_tokens":max_tokens}
    accept = 'application/json'
    contentType = 'application/json'

    response = boto3_bedrock.invoke_model(
        body=json.dumps(body), 
        modelId=model_id, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    assistant_text = response_body.get("content")[0].get("text")
    new_history = add_text("assistant", assistant_text, new_history)
    return assistant_text, new_history

def get_agent_response(session_id, prompt,history):

    """
    Sends a prompt for the agent to process and respond to.

    :param agent_id: The unique identifier of the agent to use.
    :param agent_alias_id: The alias of the agent to use.
    :param session_id: The unique identifier of the session. Use the same value across requests
        to continue the same conversation.
    :param prompt: The prompt that you want Claude to complete.
    :return: Inference response from the model.
    """

    try:
        
        #history
        content = [{"type":"text","text":prompt}]
        new_history = add_text("user",content, history)
        
        # Note: The execution time depends on the foundation model, complexity of the agent,
        # and the length of the prompt. In some cases, it can take up to a minute or more to
        # generate a response.
        # Obtener la versión de boto3
        
        boto3_version = getattr(boto3, '__version__', 'Unknown version')
    
        # Imprimir la versión en los logs
        print(f'Boto3 version: {boto3_version}')

        print("Invocando al agente")
        print(prompt)
        print(agentId)
        print(session_id)
        print(agentAliasId)


        bedrock_client = boto3.client("bedrock-agent-runtime")
        response = bedrock_client.invoke_agent(
            agentAliasId = agentAliasId,
            agentId = agentId,
            enableTrace = True,
            endSession = False,
            inputText = prompt,
            sessionId = session_id
        )

        print(response)

        # Leer la respuesta del agente
        try:
            completion = ""

            for event in response['completion']:
                if isinstance(event, dict):
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'text' in chunk:
                            print(chunk['text'])
                            completion = completion + chunk['text']
                        elif 'bytes' in chunk:
                            print(chunk['bytes'].decode('utf-8'))
                            completion = completion + chunk['bytes'].decode('utf-8')
                    elif 'bytes' in event:
                        print(event['bytes'].decode('utf-8'))
                        completion = completion + chunk['bytes'].decode('utf-8')
                else:
                    print(event)
                
                print('completion:')
                print(completion)

        except KeyError as e:
            print(f"KeyError: {e}")

    except  :
        print("Couldn't invoke agent. ")
        raise

    new_history = add_text("assistant", completion, new_history)

    return completion,new_history

def lambda_handler(event, context):
    print (event)

    whats_message = event['whats_message']
    print(whats_message)
    print('REQUEST RECEIVED:', event)
    print('REQUEST CONTEXT:', context)
    print("PROMPT: ",whats_message)

    try:
        whats_token = event['whats_token']
        messages_id = event['messages_id']
        phone = event['phone']
        phone_id = event['phone_id']
        phone_number = phone.replace("+","")
        
        session_data = query("phone_number",table_session_active,phone_number)
        now = int(time.time())
        diferencia = now - session_data["session_time"]
        if diferencia > 240:  #session time in seg
            print("Mayor de 240")
            update_item_session(table_session_active,phone_number,now)
            id = str(phone_number) + "_" + str(now)
            history = []
        else:
            print("Menor de 240")
            id = str(phone_number) + "_" + str(session_data["session_time"])
            history = query_history("SessionId",table_name_session,id)["History"]
            print(history)
           
    except:
        print("Nuevo")
        now = int(time.time())
        new_row = {"phone_number": phone_number, "session_time":now}
        save_item_ddb(table_session_active,new_row)
        history = []
        id = str(phone_number) + "_" + str(now)

    try:
       
        whats_token = event['whats_token']
        messages_id = event['messages_id']
        phone = event['phone']
        phone_id = event['phone_id']

        max_tokens=1000
        response,history =  get_agent_response(messages_id,whats_message,history) #agent_text(model_id, anthropic_version, whats_message, max_tokens,history)
        print(response)

        whats_reply(whatsapp_out_lambda,phone, whats_token, phone_id, f"{response}", messages_id)
        end = int( time.time())
        update_items_out(table,messages_id,response,end)
        
        item = {"SessionId":id,"History" : history}
        save_history(table_name_session,item)

        return({"body":response})   
    
    except Exception as error: 
        print('FAILED!', error)
        return({"body":"Cuek! I dont know"})