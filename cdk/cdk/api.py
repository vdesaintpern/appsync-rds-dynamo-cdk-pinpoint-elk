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

class Api:

    # Exported entities
    lambda_security_group = None
    lambda_rds_resolver = None
    vote_table = None
    lambda_votes_dynamodb_resolver = None
    api = None
    api_key = None
    products_ds = None
    votes_ds = None
    votes_dynamo_ds = None
    vote_up_resolver=None
    vote_down_resolver=None

    # factory pattern, return object instance
    @classmethod
    def build(cls, *, stack, vpc_db_instance):

        api = cls()

        api._build_dynamodb_vote_table(stack=stack)

        api._build_api(stack=stack)

        api._build_app_sync_rds_resolver(stack=stack, vpc_db_instance=vpc_db_instance)

        api._build_votes_field_lambda_resolver(stack=stack)

        api._build_votes_mutation_direct_resolver_pipeline(stack=stack)

        return api

    def _build_dynamodb_vote_table(self, *, stack):

        self.vote_table = ddb.Table(stack, 'votes', 
            table_name='votes', 
            partition_key={
                "name": "productid",
                "type": ddb.AttributeType.STRING
            }, 
            # Sortkey structure is like : UP#20200902T12:34:00 - DOWN#20201030T10:45:12
            sort_key={
                "name": "votesortkey",
                "type": ddb.AttributeType.STRING
            },
            read_capacity=5, 
            write_capacity=5
        )

    def _build_api(self, *, stack):

        self.api = appsync.GraphqlApi(stack, 'exampleapi',
                                name="examplegraphqlapi",
                                log_config=appsync.LogConfig(field_log_level=appsync.FieldLogLevel.ALL),
                                schema=appsync.Schema.from_asset(file_path="../appsync-conf/schema.graphql")
                                )

        self.api_key = appsync.CfnApiKey(stack, 'examplegraphqlapi',
                                    api_id=self.api.api_id
                                    )

    def _build_app_sync_rds_resolver(self, *, stack, vpc_db_instance):

        self.lambda_security_group = ec2.SecurityGroup(stack, "AppSyncResolverLambdaSG", 
            security_group_name="AppSyncResolverLambdaSG",
            vpc=vpc_db_instance.vpc,
            allow_all_outbound=True
        )

        vpc_db_instance.db_security_group.add_ingress_rule(self.lambda_security_group, ec2.Port.tcp(5432), 'lambda resolver')

        app_code = aws_lambda.Code.asset("../lambdas/lambda-resolver")

        self.lambda_rds_resolver = aws_lambda.Function(stack,
            "LambdaAppSyncSQLResolver",
            function_name=f"LambdaAppSyncSQLResolver",
            code=app_code,
            handler="index.handler",
            runtime=aws_lambda.Runtime.NODEJS_12_X,
            memory_size=512,
            timeout=core.Duration.seconds(60),
            log_retention=logs.RetentionDays.ONE_MONTH,
            vpc=vpc_db_instance.vpc,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.PRIVATE
            },
            security_group=self.lambda_security_group,
        )

        self.lambda_rds_resolver.add_environment("ENDPOINT", vpc_db_instance.db_instance.db_instance_endpoint_address)
        self.lambda_rds_resolver.add_environment("DATABASE", 'exampledb')
        self.lambda_rds_resolver.add_environment("SECRET_ARN", vpc_db_instance.db_instance.secret.secret_arn)

        self.lambda_rds_resolver.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[ 'secretsmanager:GetSecretValue' ],
            resources=[ vpc_db_instance.db_instance.secret.secret_arn ]
        ))

        self.products_ds = self.api.add_lambda_data_source('Products', self.lambda_rds_resolver)

        self.products_ds.create_resolver(
            type_name='Query',
            field_name='getProducts',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/getProducts.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/getProducts_output_template.vtl"),
        )

        self.products_ds.create_resolver(
            type_name='Query',
            field_name='getProduct',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/getProduct.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/getProduct_output_template.vtl"),
        )

    def _build_votes_field_lambda_resolver(self, *, stack):

        app_code_votes = aws_lambda.Code.asset("../lambdas/lambda-votes-resolver")

        self.lambda_votes_dynamodb_resolver = aws_lambda.Function(stack,
            "LambdaAppSyncVotesResolver",
            function_name=f"LambdaAppSyncVotesResolver",
            code=app_code_votes,
            handler="index.handler",
            runtime=aws_lambda.Runtime.NODEJS_12_X,
            memory_size=128,
            timeout=core.Duration.seconds(60),
        )

        self.lambda_votes_dynamodb_resolver.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[ 
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem" 
            ],
            resources=[ 
                self.vote_table.table_arn,
                self.vote_table.table_arn + "/*"
            ]
        ));           

        self.votes_ds = self.api.add_lambda_data_source('Votes', self.lambda_votes_dynamodb_resolver)

        self.votes_ds.create_resolver(
            type_name='Product',
            field_name='ups',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/fields/votes_up.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/fields/votes_up_output_template.vtl"),
        )

        self.votes_ds.create_resolver(
            type_name='Product',
            field_name='downs',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/fields/votes_down.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/fields/votes_down_output_template.vtl"),
        )

    def _build_votes_mutation_direct_resolver_pipeline(self, *, stack):
        
        self.votes_dynamo_ds = self.api.add_dynamo_db_data_source('vote_direct_dynamo', table=self.vote_table)    

        voteUpFunction = appsync.CfnFunctionConfiguration(stack, 'voteupstore',
            api_id=self.api.api_id, 
            data_source_name=self.votes_dynamo_ds.name, 
            function_version="2018-05-29",
            name='voteupstore',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/function_voteup.vtl").render_template(),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/function_voteup_output_template.vtl").render_template(),
        )

        voteDownFunction = appsync.CfnFunctionConfiguration(stack, 'votedownstore',
            api_id=self.api.api_id, 
            data_source_name=self.votes_dynamo_ds.name, 
            function_version="2018-05-29",
            name='votedownstore',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/function_votedown.vtl").render_template(),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/function_votedown_output_template.vtl").render_template(),
        )

        getProductFunction = appsync.CfnFunctionConfiguration(stack, 'getproductbyid',
            api_id=self.api.api_id, 
            data_source_name=self.products_ds.name, 
            function_version="2018-05-29",
            name='getproductbyid',
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/getProduct.vtl").render_template(),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/queries/getProduct_output_template.vtl").render_template(),
        )

        self.vote_up_resolver = appsync.Resolver(stack, 'voteUpResolver',
            api=self.api,
            type_name='Mutation',
            field_name='voteUp',
            pipeline_config=[
                voteUpFunction.attr_function_id,
                getProductFunction.attr_function_id
            ],
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/pipeline_resolver_votes_up.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/pipeline_resolver_votes_up_output_template.vtl")
        )

        self.vote_down_resolver = appsync.Resolver(stack, 'voteDownResolver',
            api=self.api,
            type_name='Mutation',
            field_name='voteDown',
            pipeline_config=[
                voteDownFunction.attr_function_id,
                getProductFunction.attr_function_id
            ],
            request_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/pipeline_resolver_votes_up.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("../appsync-conf/vtl/product/mutations/pipeline_resolver_votes_up_output_template.vtl")
        )

        voteUpFunction.add_depends_on(self.votes_dynamo_ds.ds)
        voteDownFunction.add_depends_on(self.votes_dynamo_ds.ds)
        getProductFunction.add_depends_on(self.products_ds.ds)