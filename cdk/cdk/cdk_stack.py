from aws_cdk import (
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_secretsmanager as sc,
    aws_rds as rds,
    aws_logs as logs,
    aws_lambda as aws_lambda,
    aws_iam as iam,
    aws_appsync as appsync,
    aws_pinpoint as pinpoint,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_elasticsearch as es,
    aws_kinesisfirehose as kfh,
    aws_cloudwatch as cw,
    aws_logs as logs,
    aws_dynamodb as ddb,
    core
)
import json
from .vpc_db import VpcDb
from .analytics import Analytics
from .api import Api

# Entry point for the stack
# this can be refactored into multiple stacks if needed

class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc_db_instance = VpcDb.build(stack=self)
        analytics_instance = Analytics.build(stack=self, vpc_db_instance=vpc_db_instance)
        api_instance = Api.build(stack=self, vpc_db_instance=vpc_db_instance)

        # Outputs
        core.CfnOutput(self, 'Endpoint', value=api_instance.api.graphql_url)
        core.CfnOutput(self, 'API_Key', value=api_instance.api.api_key)
        core.CfnOutput(self, 'CognitoID', value=analytics_instance.cognito_identity_pool.ref)
        core.CfnOutput(self, 'PinPointID', value=analytics_instance.pinpoint_instance.ref)



