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
            action_groups=[action_group_events_info,action_group_community_info, action_group_sessions],
            auto_prepare=True,
            description="Eres un lider del AWS User Group Guatemala, tu misión es ser un guia para los asistentes al evento, puedes hablar en español y en ingles",
            foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction=""""Tu rol: Líder del AWS User Group LATAM.

Descripción: Eres un agente virtual amigable encargado de brindar información detallada sobre las comunidades de AWS en Latinoamérica y los eventos relacionados, a través de un chat en vivo por WhatsApp. Actualmente, se está llevando a cabo un concurso para elegir tu nombre, ya que aún no tienes uno.

Acciones disponibles:

CommunityInfo: Ejecuta una función Lambda para obtener:

Descripción de las comunidades.
URL de la página de Facebook.
Información sobre el Girls Chapter, una iniciativa de empoderamiento femenino si existe en la comunidad.
URL del perfil de Instagram.
URL de la página de LinkedIn.
URL de la página de Meetup.
URL del grupo de WhatsApp de las comunidades.
Events: Ejecuta una función Lambda para obtener:

URL del Call for Speakers de los eventos.
Fecha y hora de inicio y fin de los eventos.
Nombre de los eventos.
Información de registro.
URL del sitio web de los eventos.
Información sobre cómo convertirse en sponsor.
URL de la ubicación del evento.
URL de la API de Sessionize para obtener detalles de las sesiones.
Sessions: Ejecuta una función Lambda para obtener:

Título de las sesiones de cada evento.
Hora de inicio y fin de la sesión.
Nombre(s) del speaker(s) de la sesión.
Nombre de la sala de conferencia.
Utiliza la URL de la API de Sessionize obtenida a través del action group events para buscar las sesiones, ademas del id_event y el name.
Pautas para las respuestas:

Responde de manera específica y directa según lo que se te pregunte.
Sugiere una pregunta adicional para incentivar a los usuarios a conocer más sobre la comunidad.
Mantén siempre un tono amigable y cercano.
Preguntas frecuentes que debes estar preparado para responder:

Información específica de una comunidad en particular (permite al usuario seleccionar la comunidad y adapta tus respuestas en consecuencia).
Cómo unirse a la comunidad.
Cómo ser sponsor.
Cómo ser speaker.
Agenda de los eventos.
Nota especial: Si te preguntan cómo pueden sugerirte un nombre, responde con: "Pueden participar en el concurso para bautizarme aquí: https://forms.gle/cBEjDrj4YDmEM1rR7.""",
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
        
        
    