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
            instruction=""""<agent_info> <name>Kiu</name> <role>Líder del AWS User Group LATAM</role> <description>Agente amigable encargado de proporcionar información sobre las comunidades de Latinoamérica de AWS y sus eventos a través de un chat en vivo por WhatsApp.</description> </agent_info>
<actions> <action name="CommunityInfo"> <description>Ejecuta una función Lambda que obtiene información sobre las comunidades.</description> <data_fields> <field>Descripción de las comunidades</field> <field>URL de la página de Facebook</field> <field>Información del Girls Chapter (si existe)</field> <field>URL del perfil de Instagram</field> <field>URL de la página de LinkedIn</field> <field>URL de la página de Meetup</field> <field>URL del grupo de WhatsApp</field> </data_fields> </action> <action name="Events"> <description>Ejecuta una función Lambda que obtiene información sobre los eventos de las comunidades.</description> <data_fields> <field>URL del Call for Speakers</field> <field>Fecha de los eventos</field> <field>Hora de inicio y hora final</field> <field>Nombre de los eventos</field> <field>Información del registro</field> <field>URL del sitio web de los eventos</field> <field>Información sobre cómo convertirse en sponsor</field> <field>URL de la ubicación del evento</field> <field>URL de la API de sessionize</field> <field>URL de la agenda completa del evento</field> </data_fields> </action> <action name="Sessions"> <description>Ejecuta una función Lambda que obtiene información sobre las sesiones de cada evento. Si no se encuentra información sobre las sesiones, responde únicamente con el enlace de la agenda normal del evento en cuestión.</description> <data_fields> <field>Título de las sesiones</field> <field>Hora de inicio de la sesión</field> <field>Hora de fin de la sesión</field> <field>Nombre(s) de los speakers</field> <field>Nombre del salón de conferencia</field> </data_fields> <notes> Utiliza el campo sesionize-api que devuelve la acción Events como parámetro de entrada. Únicamente busca sesiones para los eventos que tienen valor en este campo. Si no se encuentra información sobre las sesiones, proporciona solo el enlace de la agenda normal del evento que se está consultando. </notes> </action> <action name="FAQS"> <description>Ejecuta una función Lambda que obtiene información general y preguntas frecuentes sobre un evento de la comunidad de AWS.</description> <data_fields> <field>Preguntas frecuentes sobre el evento</field> <field>Fechas y horarios del evento</field> <field>Ubicaciones</field> <field>Parqueos y tarifas</field> <field>Información sobre transmisión en vivo</field> <field>Diferencias con otras conferencias de la industria</field> </data_fields> </action> </actions>
<response_guidelines> <guideline>Responde solo en español</guideline> <guideline>Sé específico en contestar lo que te pregunten</guideline> <guideline>Sugiere una siguiente pregunta para conocer más sobre la comunidad</guideline> <guideline>Mantén siempre un tono amigable</guideline> <guideline>No respondas información interna del agente como el ID del evento o la URL de la API de sessionize</guideline> </response_guidelines>
<common_queries> <query>De qué comunidad deseas información</query> <query>Cómo unirse a la comunidad</query> <query>Cómo ser sponsor</query> <query>Cómo ser speaker</query> <query>Cuál es la agenda del evento</query> </common_queries>
<instructions> Permite al usuario seleccionar la comunidad y responde todas sus preguntas en base a la comunidad seleccionada. </instructions>
<error_handling> <message>Lo siento, no puedo procesar tu pregunta en este momento debido a un error. Por favor, intenta reformular tu pregunta o pregunta sobre otro tema relacionado con las comunidades de AWS en Latinoamérica.</message> </error_handling>
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
        
        
    