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

class Analytics:

    # Exported resources created
    pinpoint_instance = None
    default_policy_cognito_identity_pool = None
    cognito_identity_pool = None
    unauthenticatedRole = None
    elastic_policy = None
    elastic_document = None
    es_security_group = None
    kfh_security_group = None
    elastic_search = None
    firehose_bucket = None
    lambda_transform_fn = None
    kfh_log_group = None
    kfh_es_log_stream = None
    kfh_instance = None
    pinpoint_firehose_role = None
    pinpoint_to_kfh = None

    # factory pattern, return object instance
    @classmethod
    def build(cls, *, stack, vpc_db_instance):

        analytics = cls()

        analytics.pinpoint_instance = pinpoint.CfnApp(stack, 'pinpoint', name="pinpoint")

        analytics._build_cognito(stack=stack)
        
        analytics._build_elastic_search(stack=stack, vpc_db_instance=vpc_db_instance)
        
        analytics.firehose_bucket = s3.Bucket(stack, 'firehose-es-bucket')
        
        analytics._build_lambda_firehose_transform(stack=stack)
        
        analytics._build_firehose_role(stack=stack)
        
        analytics._build_firehose_delivery_stream(stack=stack, vpc_db_instance=vpc_db_instance)
        
        analytics._grant_transform_lambda_access_to_delivery_stream(stack=stack)
        
        analytics._connect_pinpoint_to_firehose_delivery_stream(stack=stack)

        return analytics

    def _build_cognito(self, *, stack):

        self.cognito_identity_pool = cognito.CfnIdentityPool(stack, 'identitypool', allow_unauthenticated_identities=True)

        self.unauthenticatedRole = iam.Role(stack, 'CognitoDefaultUnauthenticatedRole',
            assumed_by=iam.FederatedPrincipal('cognito-identity.amazonaws.com', {
                "StringEquals": { 
                    "cognito-identity.amazonaws.com:aud": self.cognito_identity_pool.ref 
                },
                "ForAnyValue:StringLike": { 
                    "cognito-identity.amazonaws.com:amr": "unauthenticated" 
                },
            }, "sts:AssumeRoleWithWebIdentity")
        )

        self.unauthenticatedRole.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "mobiletargeting:PutEvents",
                "mobiletargeting:GetUserEndpoints",
                "mobiletargeting:UpdateEndpoint"
            ],
            resources=[self.pinpoint_instance.attr_arn + "/*"]
        ))

        self.unauthenticatedRole.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "mobileanalytics:PutEvents",
                # TODO : least privileged 
                "cognito-sync:*"
            ],
            resources=["*"]
        ))

        self.default_policy_cognito_identity_pool = cognito.CfnIdentityPoolRoleAttachment(stack, 'identitypoolrolatt',
            identity_pool_id=self.cognito_identity_pool.ref,
            roles= {
                'unauthenticated': self.unauthenticatedRole.role_arn,
                # If you need authenticated users, you need to have a separate role
                # Here, both have the same
                'authenticated': self.unauthenticatedRole.role_arn
            }
        )

    def _build_elastic_search(self, *, stack, vpc_db_instance):

        # example in https://github.com/aws-samples/aws-cdk-managed-elkk
        # TODO: fine-tune policies for data access
        self.elastic_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW, actions=["es:*",], resources=["*"],
        )
        self.elastic_policy.add_any_principal()
        self.elastic_document = iam.PolicyDocument()
        self.elastic_document.add_statements(self.elastic_policy)

        self.es_security_group = ec2.SecurityGroup(stack, "BastiontoES", 
            security_group_name="BastiontoES",
            vpc=vpc_db_instance.vpc,
            allow_all_outbound=True
        )

        self.kfh_security_group = ec2.SecurityGroup(stack, "KFHtoES", 
            security_group_name="KFHtoES",
            vpc=vpc_db_instance.vpc,
            allow_all_outbound=True
        )

        self.es_security_group.add_ingress_rule(vpc_db_instance.bastion_host_security_group, ec2.Port.tcp(443), 'es')
        self.es_security_group.add_ingress_rule(self.kfh_security_group, ec2.Port.tcp(443), 'kfh')

        self.elastic_search = es.CfnDomain(stack, 'exampledomain', 
            domain_name='exampledomaines',
            elasticsearch_cluster_config={
                "instanceCount": 1,
                "instanceType": 't2.small.elasticsearch'
            },
            elasticsearch_version="7.7",
            ebs_options={"ebsEnabled": True, "volumeSize": 10},
            vpc_options={
            
                "securityGroupIds": [self.es_security_group.security_group_id],
                "subnetIds": [vpc_db_instance.vpc.select_subnets(
                        subnet_type=ec2.SubnetType.PRIVATE
                    ).subnet_ids[0]]
                },
            
            access_policies=self.elastic_document)
    
    def _build_lambda_firehose_transform(self, *, stack):

        app_transform_code = aws_lambda.Code.asset("../lambdas/lambda-transform")

        self.lambda_transform_fn = aws_lambda.Function(stack,
            "LambdaKFHTransformer",
            function_name=f"LambdaKFHTransformer",
            code=app_transform_code,
            handler="index.handler",
            runtime=aws_lambda.Runtime.NODEJS_12_X,
            memory_size=128,
            timeout=core.Duration.seconds(60),
            log_retention=logs.RetentionDays.ONE_MONTH
        )

    def _build_firehose_role(self, *, stack):
    
        self.firehose_role = iam.Role(stack, 'FirehoseElasticSearchRole',
            assumed_by=iam.ServicePrincipal('firehose.amazonaws.com')
        )

        # TODO : Could be split in 2 roles : 1 for ES, 1 for S3
        self.firehose_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:AbortMultipartUpload",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:PutObject"
            ],
            resources=[self.firehose_bucket.bucket_arn + "/*", self.firehose_bucket.bucket_arn]
        ))

        self.firehose_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "es:DescribeElasticsearchDomain",
                "es:DescribeElasticsearchDomains",
                "es:DescribeElasticsearchDomainConfig",
                "es:ESHttpPost",
                "es:ESHttpPut",
                # TODO : least privileged
                "es:ESHttpGet"
            ],
            resources=[self.elastic_search.attr_arn + "/*", self.elastic_search.attr_arn]
        ))

        # TODO : Access to many things in the VPC, limit these to the VPC you want
        self.firehose_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "ec2:CreateNetworkInterface",
                "ec2:CreateNetworkInterfacePermission",
                "ec2:Describe*",
                "ec2:DeleteNetworkInterface"
            ],
            resources=['*']
        ))

        self.firehose_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:PutLogEvents"
            ],
            # TODO : parameters
            resources=["arn:aws:logs:<region>:<aws_account>:log-group:/aws/kinesisfirehose/exampledeliverystream:log-stream:*"]
        ))

        self.firehose_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "lambda:InvokeFunction",
                "lambda:GetFunctionConfiguration"
            ],
            resources=[self.lambda_transform_fn.function_arn + ":$LATEST"]
        ))

    def _build_firehose_delivery_stream(self, *, stack, vpc_db_instance):
    
        self.kfh_log_group=logs.LogGroup(stack, "exampledeliverystreamloggroup",
                log_group_name="/aws/kinesisfirehose/exampledeliverystream")

        self.kfh_es_log_stream=logs.LogStream(stack, "deliverytoeslogstream",
                log_stream_name="deliverytoes",
                log_group=self.kfh_log_group)
        

        self.kfh_instance = kfh.CfnDeliveryStream(stack, 'exampledeliverystream',
            delivery_stream_type='DirectPut',
            elasticsearch_destination_configuration={
                "indexName": "webappclickstream",
                "cloudwatch_logging_options": {
                    "Enabled": True,
                    "LogGroupName": "exampledeliverystream",
                    "LogStreamName": "deliverytoes"
                },
                "roleArn": self.firehose_role.role_arn,
                "s3Configuration": {
                    "bucketArn": self.firehose_bucket.bucket_arn,
                    "roleArn": self.firehose_role.role_arn
                },            
                "domainArn": self.elastic_search.attr_arn,
                "vpcConfiguration": {
                    "roleArn": self.firehose_role.role_arn,
                    "securityGroupIds": [self.kfh_security_group.security_group_id],
                    "subnetIds": [vpc_db_instance.vpc.select_subnets(
                        subnet_type=ec2.SubnetType.PRIVATE
                    ).subnet_ids[0]]   
                },
                "bufferingHints": {
                    "intervalInSeconds": 60,
                    "sizeInMBs": 1
                }, 
                "ProcessingConfiguration": {
                    "enabled": True,
                    "Processors": []
                },
                "ProcessingConfiguration": {
                    "Enabled": "true",
                    "Processors": [
                        {
                            "Parameters": [ 
                                { 
                                    "ParameterName": "LambdaArn",
                                    "ParameterValue":  self.lambda_transform_fn.function_arn
                                }
                            ],
                            "Type": "Lambda"
                        }
                    ]
                }
            }
        )

    def _grant_transform_lambda_access_to_delivery_stream(self, *, stack):
        
        # this is important so that Lambda can read in the stream
        self.lambda_transform_fn.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[ 'kinesis:DescribeStream',
                'kinesis:DescribeStreamSummary',
                'kinesis:GetRecords',
                'kinesis:GetShardIterator',
                'kinesis:ListShards',
                'kinesis:ListStreams',
                'kinesis:SubscribeToShard'
            ],
            resources=[ self.kfh_instance.attr_arn ]
        ))

    def _connect_pinpoint_to_firehose_delivery_stream(self, *, stack):
        
        self.pinpoint_firehose_role = iam.Role(stack, 'PinPointToFirehoseRole',
            assumed_by=iam.ServicePrincipal('pinpoint.amazonaws.com')
        )

        self.pinpoint_firehose_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "firehose:PutRecordBatch",
                "firehose:DescribeDeliveryStream"
            ],
            resources=[self.kfh_instance.attr_arn]
        ))

        self.pinpoint_to_kfh = pinpoint.CfnEventStream(stack, 'pinpointclickstreamtokfh',
            application_id=self.pinpoint_instance.ref,
            destination_stream_arn=self.kfh_instance.attr_arn,
            role_arn=self.pinpoint_firehose_role.role_arn
        )