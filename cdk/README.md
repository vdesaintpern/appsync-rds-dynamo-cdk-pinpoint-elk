
## CDK Infrastructure-as-code

### Context

CDK folder contains infrastructure-as-code written in Python.
CDK will execute these files and provision the resources.

### Initialisation
Folder has been initialized with
cdk init app --language python

Virtual env has been created with :
python3 -m venv .env

Activation of virtualenv with : 
source .env/bin/activate

Python requirements are in the setup.py.
it's referenced in the requirements.txt through the '-e .' command.

Install python requirements with
python -m pip install -r requirements.txt

CDK bootstrap is required when deploying to new account / region :
cdk bootstrap aws://<aws_account>/<region>

### Operations

Before deploying anything, it's good practice to run 'cdk synth'. This will help you with potential errors.

You can also go 'cdk diff' which will synth + diff. This helps you see what will be done before it's actually done.

When you're good : 'cdk deploy'

## Database 

CDK Script creates a PostGreSQL database. 
A Secret in AWS Secrets manager is provisionned (db password).
To connect, you can use a SSH tunnel. (see ssh-tunnel folder)
Admin user name is set to 'exampleadmin'
Use the SQL script provided to create the sample database. (see sql folder)

## Lambdas

2 Lambdas have dependancies : lambda-resolver and lambda-vote-resolver.
run 'npm install' in the lambda folders to make sure the dependancies are downloaded.

