#################################################
## This function is to query a dynamoDB table ###
#################################################

import json
import boto3
import os
import requests
import time

from db_utils import query,save_item_ddb,update_items_out,update_item_session

from langchain.chains import ConversationChain

from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.llms.bedrock import Bedrock
from boto3.dynamodb.conditions import Key
from utils import ( normalize_phone,whats_reply)

client_s3 = boto3.client('s3')
dynamodb_resource=boto3.resource('dynamodb')
bedrock_client = boto3.client("bedrock-runtime")

whatsapp_out_lambda = os.environ.get('WHATSAPP_OUT')

agentId=os.environ.get('agentId')
agentAlias = os.environ.get('agentAliasId').split('|')
agentAliasId=agentAlias[1]

table_name_active_connections = os.environ.get('whatsapp_MetaData')

table_session_active = dynamodb_resource.Table(os.environ['user_sesion_metadata'])
table_name_session = os.environ.get('session_table_history')

base_path="/tmp/"
model_id = os.environ.get('ENV_MODEL_ID')

table = dynamodb_resource.Table(table_name_active_connections)


model_parameter = {"temperature": 0.0, "top_p": .9, "max_tokens_to_sample": 2000}
llm = Bedrock(model_id=model_id, model_kwargs=model_parameter,client=bedrock_client)

def memory_dynamodb(id,table_name_session):
    message_history = DynamoDBChatMessageHistory(table_name=table_name_session, session_id=id)
    memory = ConversationBufferMemory(
        memory_key="history", chat_memory=message_history, return_messages=True,ai_prefix="A",human_prefix="H"
    )
    return memory


def get_chat_response(llm,prompt, memory):
    
    conversation_with_summary = ConversationChain( #create a chat client
        llm = llm, #using the Bedrock LLM
        memory = memory, #with the summarization memory
        verbose = True #print out some of the internal states of the chain while running
    )
    conversation_with_summary.prompt.template ="""The following is a friendly conversation between a human and an AI. 
    The AI is talkative and provides lots of specific details from its context. 
    If the AI does not know the answer to a question, it truthfully says it does not know.
    Always reply in the original user language.

    Current conversation:
    {history}

    Human:{input}

    Assistant:"""
    return conversation_with_summary.predict(input=prompt)



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
        content = [{"type":"text","text":prompt}]
        #new_history = add_text("user",content, history)
        
        # Note: The execution time depends on the foundation model, complexity of the agent,
        # and the length of the prompt. In some cases, it can take up to a minute or more to
        # generate a response.
        # Obtener la versión de boto3

        print(prompt)
        print(agentAliasId)
        print(agentId)
        print(session_id)

        boto3_version = getattr(boto3, '__version__', 'Unknown version') 

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
        print("Couldn't invoke agent. *** ")
        raise

    #new_history = add_text("assistant", completion, new_history)

    return completion#,new_history


def lambda_handler(event, context):
    print (event)

    whats_message = event['whats_message']
    print(whats_message)

    whats_token = event['whats_token']
    messages_id = event['messages_id']
    phone = event['phone']
    phone_id = event['phone_id']
    phone_number = phone.replace("+","")

    #The session ID is created to store the history of the messages. 

    try:
        session_data = query("phone_number",table_session_active,phone_number)
        now = int(time.time())
        diferencia = now - session_data["session_time"]
        if diferencia > 240:  #session time in seg
            update_item_session(table_session_active,phone_number,now)
            id = str(phone_number) + "_" + str(now)
        else:
            id = str(phone_number) + "_" + str(session_data["session_time"])

    except:
        now = int(time.time())
        new_row = {"phone_number": phone_number, "session_time":now}
        save_item_ddb(table_session_active,new_row)
        
        id = str(phone_number) + "_" + str(now)

    try:
        print('REQUEST RECEIVED:', event)
        print('REQUEST CONTEXT:', context)
        print("PROMPT: ",whats_message)

        #s = re.sub(r'[^a-zA-Z0-9]', '', query)

        memory = memory_dynamodb(id,table_name_session)

        response =get_agent_response(memory,whats_message) #get_agent_response(memory,whats_message);

        #response = get_chat_response(llm,whats_message, memory)

        print(response)

        whats_reply(whatsapp_out_lambda,phone, whats_token, phone_id, f"{response}", messages_id)
        
        end = int( time.time())

        update_items_out(table,messages_id,response,end)
                
        return({"body":response})
        
        
    except Exception as error: 
            print('FAILED!', error)
            return({"body":"Cuek! I dont know"})

