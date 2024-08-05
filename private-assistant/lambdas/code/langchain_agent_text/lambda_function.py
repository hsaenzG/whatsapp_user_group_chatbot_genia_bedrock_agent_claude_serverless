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


def get_agent_response(session_id, prompt):

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
        #content = [{"type":"text","text":prompt}]
        #new_history = add_text("user",content, history)
        
        # Note: The execution time depends on the foundation model, complexity of the agent,
        # and the length of the prompt. In some cases, it can take up to a minute or more to
        # generate a response.
        # Obtener la versión de boto3
        
        print("llamando agente")

        bedrock_client = boto3.client("bedrock-agent-runtime")
        response = bedrock_client.invoke_agent(
            agentAliasId = agentAliasId,
            agentId = agentId,
            enableTrace = True,
            endSession = False,
            inputText = prompt,
            sessionId = session_id
        )

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

    return completion

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
        else:
            print("Menor de 240")
           
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
        response =  get_agent_response(messages_id,whats_message) 
        print(response)

        whats_reply(whatsapp_out_lambda,phone, whats_token, phone_id, f"{response}", messages_id)
        end = int( time.time())
        update_items_out(table,messages_id,response,end)
        

        return({"body":response})   
    
    except Exception as error: 
        print('FAILED!', error)
        return({"body":"Cuek! I dont know"})