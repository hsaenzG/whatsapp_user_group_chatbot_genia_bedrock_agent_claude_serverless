from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_bedrock as bedrock,
)
import os
from constructs import Construct
import json

class bedrock_agents(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    def create_agent(self, agent_name: str,  lambda_function_name_event: str,lambda_function_name_community: str) -> bedrock.CfnAgent:
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

        # At long last, create the bedrock agent!
        self.BedrockAgent = cfn_agent = bedrock.CfnAgent(
            self,
            "AWSCommunityLeaderAgent",
            agent_name=agent_name,
            # the properties below are optional
            action_groups=[action_group_events_info,action_group_community_info],
            auto_prepare=True,
            description="Eres un lider del AWS User Group Guatemala, tu misión es ser un guia para los asistentes al evento, puedes hablar en español y en ingles",
            foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction=""""
                    Tu nombre es Claude, tu rol es lider del AWS User Group Guatemala, eres un agente el cual se encarga de dar información de los eventos de la comunidad, 
                    para obtener la información sobre la comunidad y como las personas se pueden unir a ella utilizarás la accion communityInfo, para obtener la información de 
                    los eventos de la comunidad utilizaras la accion events.
                    Se especifico en contestar lo que te pregunten y sugiere una siguiente pregunta para conocer un poco mas sobre la comunidad.
                    Devuelve toda esta información en un tono amigable. 
                    Responde únicamente preguntas relacionadas con el AWS User Group Guatemala""",
            agent_resource_role_arn=agent_role.role_arn,
        )
        """
        An alias points to a specific version of your Agent. Once you create and associate a version with an alias, you can test it. 
        With an alias, you can also update the Agent version that your client applications use.
        """
        agent_alias = bedrock.CfnAgentAlias(
            self,
            "awsLeaderAgentAlias",
            agent_alias_name="awsLeaderAgent",
            agent_id=cfn_agent.attr_agent_id,
        )

        return cfn_agent.attr_agent_id, agent_alias.ref
        
        
    