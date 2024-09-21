from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_bedrock as bedrock,
)
import os
from constructs import Construct
import json
import datetime

class bedrock_agents(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    def create_agent(self, agent_name: str,  lambda_function_name_event: str,lambda_function_name_community: str, lambda_function_name_sessions: str, lambda_function_faqs: str) -> bedrock.CfnAgent:
         # create a new bedrock agent, using Claude-3 Haiku
        agent_role = iam.Role(
            self,
            "AgentIamRole",
            role_name="AmazonBedrockExecutionRoleForAgents_",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Agent role created for community chatbot.",
        )
        # This agent has permissions to do all things Bedrock
        agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=["*"],
                resources=["arn:aws:bedrock:*"],
            )
        )
        #This is the OpenAPI that the agent will use to validate the input for the events
        with open("./lambdas/code/community_event_info/OpenAPI.json", "r") as file:
            schema = file.read()
        action_group_events_info = bedrock.CfnAgent.AgentActionGroupProperty(
            action_group_name="events",
            action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                lambda_= lambda_function_name_event
            ),
            # the properties below are optional
            api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema),
            description="Con esta acción podras obtener la información de todos los eventos organizados por la comunidad.",
            skip_resource_in_use_check_on_delete=False,
        )

        #This is the OpenAPI that the agent will use to validate the input for the community
        with open("./lambdas/code/community_info/OpenAPI.json", "r") as file:
            schema = file.read()
            action_group_community_info = bedrock.CfnAgent.AgentActionGroupProperty(
            action_group_name="communityInfo",
            action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                lambda_= lambda_function_name_community
            ),
            # the properties below are optional
            api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema),
            description="""Esta acción encontraras los datos de la comunidad, 
                    los links de las redes sociales, e información acerca del girls chapter""",
            skip_resource_in_use_check_on_delete=False,
        )
            
        #This is the OpenAPI that the agent will use to validate the input for the sessions of the community day
        with open("./lambdas/code/community_sessions/OpenAPI.json", "r") as file:
            schema = file.read()
            action_group_sessions = bedrock.CfnAgent.AgentActionGroupProperty(
            action_group_name="sessions",
            action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                lambda_= lambda_function_name_sessions
            ),
            # the properties below are optional
            api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema),
            description="""Esta acción encontrarás sesiones del Community Day, en ella podrás acceder 
                    a los títulos de las sesiones, fecha, hora cada sesión, el salón dónde se dará la sesión y el speaker""",
            skip_resource_in_use_check_on_delete=False,
        )

        #This is the OpenAPI that the agent will use to validate the input for the FAQs
        with open("./lambdas/code/get_faqs/OpenAPI.json", "r") as file:
            schema = file.read()
            action_group_faqs = bedrock.CfnAgent.AgentActionGroupProperty(
            action_group_name="faqs",
            action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                lambda_= lambda_function_faqs
            ),
            # the properties below are optional
            api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema),
            description="""Esta acción encontraras las preguntas frecuentes sobre un evento de AWS User Group""",
            skip_resource_in_use_check_on_delete=False,
        )

        # At long last, create the bedrock agent!
        self.BedrockAgent = cfn_agent = bedrock.CfnAgent(
            self,
            "AWSCommunityLeaderAgent",
            agent_name=agent_name,
            # the properties below are optional
            action_groups=[action_group_events_info,action_group_community_info, action_group_sessions,action_group_faqs],
            auto_prepare=True,
            description="Eres un lider del AWS User Group Guatemala, tu nombre es Kiu, tu misión es ser un guia para los asistentes al evento, puedes hablar solo español",
            foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="""Tu rol es líder del AWS User Group LATAM. Tu nombre es Kiu y eres un agente amigable encargado de proporcionar información sobre las comunidades de Latinoamerica de AWS y los eventos a través de un chat en vivo por WhatsApp. 
Utiliza las siguientes acciones para proporcionar la información necesaria:

CommunityInfo: Esta acción ejecuta una función Lambda que obtiene:
- La descripción de las comunidades.
- La URL de la página de Facebook de las comunidades.
- Información del Girls Chapter, una cápsula enfocada en el empoderamiento femenino si existe en la comunidad.
- La URL del perfil de Instagram.
- La URL de la página de LinkedIn.
- La URL de la página de Meetup.
- La URL del grupo de WhatsApp de las comunidades.

Events: Esta acción ejecuta una función Lambda que obtiene:
- URL del Call for Speakers de los eventos de las comunidades.
- Fecha de los eventos.
- Hora de inicio y hora final.
- El nombre de los eventos.
- Información del registro.
- URL del sitio web de los eventos.
- Información sobre cómo convertirse en sponsor.
- La URL de la ubicación del evento.
- La URL de la API de sessionize para obtener la información de las sesiones de cada evento
- La URL de la agenda completa del evento.

Pautas para las respuestas:
- Responde solo en español
- Sé específico en contestar lo que te pregunten.
- Sugiere una siguiente pregunta para conocer más sobre la comunidad.
- Mantén siempre un tono amigable.
- no respondas informacion interna del agente como el Id del evento o La URL de la API de sessionize.
Preguntas frecuentes que debes estar preparado para responder:
- De que comunidad deseas información. Permitele al usuario seleccionar la comunidad y responde todas sus respuestas en base a la comunidad seleccionada
- Cómo unirse a la comunidad.
- Cómo ser sponsor.
- Cómo ser speaker.
- Cuál es la agenda del evento.

Sessions: Esta acción ejecuta una función Lambda que obtiene:
- El título de la sesiones de cada evento.
- La hora de inicio de la sesión.
- La hora de fin de la sesión.
- Nombre o nombres de los speakers de la sesión.
- Nombre de salón de conferencia de la sesión.
- utiliza el campo sesionize-api que devuelve la action events como parametro de entrada. Unicamente busca sesiones para los eventos que tienen valor en este campo.


FAQS: Esta acción ejecuta una función Lambda que obtiene:
- Preguntas frecuentes sobre un evento de la comunidad de AWS
- Fechas y horarios del evento
- Ubicaciones
- Parqueos y tarifas
- Si el evento contara con transmisión en vivo
- En que se diferencia el evento de otras conferencias de la industria
""",
            agent_resource_role_arn=agent_role.role_arn,
        )
        """
        An alias points to a specific version of your Agent. Once you create and associate a version with an alias, you can test it. 
        With an alias, you can also update the Agent version that your client applications use.
        """

        # Obtener la fecha y hora actual
        now = datetime.datetime.now()
        # Formatear la fecha y hora como cadena
        timestamp = now.strftime("%Y%m%d_%H%M%S")



        agent_alias = bedrock.CfnAgentAlias(
            self,
            "awsLeaderAgentAlias" + timestamp,
            agent_alias_name="awsLeaderAgent" +  timestamp,
            agent_id=cfn_agent.attr_agent_id,
        )

        return cfn_agent.attr_agent_id, agent_alias.ref
        
        
    