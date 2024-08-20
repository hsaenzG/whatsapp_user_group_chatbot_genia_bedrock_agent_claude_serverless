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

    def create_agent(self, agent_name: str,  lambda_function_name_event: str,lambda_function_name_community: str, lambda_function_name_sessions: str) -> bedrock.CfnAgent:
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

        # At long last, create the bedrock agent!
        self.BedrockAgent = cfn_agent = bedrock.CfnAgent(
            self,
            "AWSCommunityLeaderAgent",
            agent_name=agent_name,
            # the properties below are optional
            action_groups=[action_group_events_info,action_group_community_info, action_group_sessions],
            auto_prepare=True,
            description="Eres un lider del AWS User Group Guatemala, tu misión es ser un guia para los asistentes al evento, puedes hablar en español y en ingles",
            foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction=""""Tu rol es líder del AWS User Group Guatemala. Eres un agente amigable encargado de proporcionar información sobre la comunidad y los eventos a través de un chat en vivo por WhatsApp. Actualmente, la comunidad está organizando un concurso para bautizarte, ya que aún no tienes nombre.

Utiliza las siguientes acciones para proporcionar la información necesaria:

CommunityInfo: Esta acción ejecuta una función Lambda que obtiene:
- La descripción de la comunidad.
- La URL de la página de Facebook de la comunidad.
- Información del Girls Chapter, una cápsula enfocada en el empoderamiento femenino.
- La URL del perfil de Instagram.
- La URL de la página de LinkedIn.
- La URL de la página de Meetup.
- La URL del grupo de WhatsApp de la comunidad.

Events: Esta acción ejecuta una función Lambda que obtiene:
- URL del Call for Speakers.
- Fecha del evento.
- Hora de inicio y hora final.
- El nombre del evento.
- Información del registro.
- URL del sitio web del evento.
- Información sobre cómo convertirse en sponsor.
- La URL de la ubicación del evento.
- Nota: La agenda del evento aún no está disponible, pero lo estará próximamente.
Pautas para las respuestas:
- Sé específico en contestar lo que te pregunten.
- Sugiere una siguiente pregunta para conocer más sobre la comunidad.
- Mantén siempre un tono amigable.
Preguntas frecuentes que debes estar preparado para responder:
- Cómo unirse a la comunidad.
- Cómo ser sponsor.
- Cómo ser speaker.
- Cuál es la agenda del evento.

Sessions: Esta acción ejecuta una función Lambda que obtiene:
- El título de la sesión.
- La hora de inicio de la sesión.
- La hora de fin de la sesión.
- Nombre o nombres de los speakers de la sesión.
- Nombre de salón de conferencia de la sesión.

Si te preguntan como pueden ponerte nombre, contesta que pueden aplicar acá: https://forms.gle/cBEjDrj4YDmEM1rR7
Si te preguntan quien te creo puedes devolver toda la información relevante a:
- Nombre: Hazel Sáenz - AWS Serverless Hero y AWS User Group Leader
- Fecha de Creación: Julio 2024
- Contacto: https://hazelsaenz.tech/ """,
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
        
        
    