# appsync-rds-dynamo-cdk-pinpoint-elk

## Scope
This repository showcases real-life end-to-end public website leveraging AWS AppSync.

## Technologies and integrations

### Databases
- PostgreSQL RDS database
- DynamoDB

### AWS AppSync configuration
- Lambda (nodeJS) with RDS
- Lambda (nodeJS) with DynamoDB using AWS SDK
- Direct DynamoDB integration
- VTL
- Field Resolvers to agreggate multiple datasources in the same entity
- Pipeline Resolvers to execute both mutation and read in 2 separate databases
- API calls from ReactJS for queries, mutations and subscriptions using Amplify codegen

### Analytics stack
- Amazon Pinpoint integration in ReactJS through AWS Amplify codegen
- Amazon ElasticSearch for further Amazon Pinpoint event analysis w/ dashboards
- Amazon PinPoint to Amazon ElasticSearch configuration through Amazon Kinesis Firehose

### General
- RDS database
- DynamoDB table
- Bastion host to connect to RDS database and Kibana through ec2 instance connect and SSH tunneling

### Infrastructure-as-code
- All code written in CDK, Cloud Development Kit in Python

## Architecture considerations

Backend and Frontend are managed in 2 separate streams :
- CDK is used to provisionned resources in the cloud
- ReactJS app uses cloud resources using Amplify JS Libs and codegen 

Pros :
- Separation of concern : 1 team can look after the backend, 1 other can look after the front end. This helps parralelize work and delegate a workstream to an external partner
- Reusability : APIs are sometimes used by more than one frontend, having a clear separation in terms of operations and code helps
- Blast radius : APIs tend to get more complicated over time and if a website developer makes a mistake, the blast radius is reduced
- Different project lifecycle : each stream can have its own pace of release and its own CI/CD
- Least privileged principle : easier to have tight policies + you can deploy the API in a AWS account and the website in another

Cons :
- Extra work if you're fullstack : using Amplify with hosting and backend features can save you time
- Managing 2 lifecycles is an overhead : you need 2 separate actions to deploy everything
- AppId, CognitoId and GraphQL ID are required to build the app

## Features showcased

- GraphQL on RDS using Lambda
- Field agregation : data coming from RDS and DynamoDB in the same type using Field Resolvers
- DynamoDB query, mutations and subscriptions with direct Resolvers and Lambda Resolvers
- VTL templates for the resolvers
- ReactJS examples of calls to the API : queries, mutations and subscriptions
- ReactJS examples of event recording in Amazon PinPoint
- Pinpoint to ElasticSearch connection through Kinesis Firehose
- Kibana dashboards leveraging events recorded in the application : sessions, page views
- Event Transformation in Kinesis Firehose
- CDK w/ Python in single stack using builder pattern
- AWS Secrets Manager for RDS database retrieval in a lambda function
- Bastion host connection to Kibana and Database through EC2 Instance Connect
- Codebuild yaml files

## Not implemented (yet)

- Multiple environnements / accounts
- Cognito user login / signup : this is unauthenticated website example
- RDS Proxy : this would help performance and load on RDS instance
- Caching AWS AppSync : this would help performance but is tighly coupled with your usecase
- Storage of Amazon Pinpoint events in a separate bucket for further analysis
- Cloudwatch dashboard and alerts
- Kibana access management and autorisations
- Encryption is not end 2 end : buckets, ElasticSearch, etc.
- Separation of CDK stack into smaller chunks

## Repository folders

### appsync-conf

GraphQL schema + VTL mapping templates are stored here. CDK code references these files.

### cdk

Everything CDK is there. This is python code. Have a look at the README for further details.

### kibana

Kibana exports of dashboards w/ screenshots.
Connec to kibana through bastion host (see ssh tunnels)

### Lambdas

3 lambdas are implemented : 
- lambda-resolver : executes the SQL queries stored in the VTL request templates
- lambda-transform : preparation of event before storage in ElasticSearch
- lambda-votes-resolver : count up and down votes from a product, integrated as a field resolver

### sql

SQL database zip file in sql format.
Simple Product table with inserts.

### ssh-tunnels

Sample scripts to create SSH tunnels from your local machine to your database or kibana through a bastion host.

### webapp

ReactJS sample application folder.
Please refer to local README for further instructions.

# Disclaimer

This code is for training purposes only and there is no garantee whatsoever.
Use it at your own risk.