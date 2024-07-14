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

    def create_agent(self, agent_name: str,  lambda_function_name: str) -> bedrock.CfnAgent:
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
         #This is the OpenAPI that the agent will use to validate the input
        with open("./lambdas/code/community_event_info/OpenAPI.json", "r") as file:
            schema = file.read()
        action_group = bedrock.CfnAgent.AgentActionGroupProperty(
            action_group_name="events",
            action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                lambda_= lambda_function_name
            ),
            # the properties below are optional
            api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema),
            description="Action that will trigger the lambda to get the events",
            skip_resource_in_use_check_on_delete=False,
        )

        # At long last, create the bedrock agent!
        self.BedrockAgent = cfn_agent = bedrock.CfnAgent(
            self,
            "AWSCommunityLeaderAgent",
            agent_name=agent_name,
            # the properties below are optional
            action_groups=[action_group],
            auto_prepare=True,
            description="Eres un lider del AWS User Group Guatemala, tu misión es ser un guia para los asistentes al evento, hablas solo español",
            foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="Eres un lider del AWS User Group Guatemala y organizador del AWS Comunity Day Guatemala 2024, presentate siempre, tu misión es ser un guia para los asistentes al evento responderas sus preguntas sobre el evento para detalles especificos del evento utilizaras la accion events en donde encontraras la información (sede,fecha, hora inicio, hora final y ubicación) de todos los eventos de la comunidad, tambien lo apoyaras a armar su agenda para el dia del evento de acuerdo a su contenido y su nivel de conocimiento, como devolver. Devuelve toda esta información en español y en un tono amigable.",
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
        
        
    