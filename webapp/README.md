# Website folder

Sample ReactJS website

### Init

Init packages with 'npm install'

Init Amplify with 'amplify init'

Index.js has parameters you have to specify from the CDK stack : AppId, CognitoId, etc

Amplify codegen setup with :
'amplify add codegen --apiId <appsyncid>'

than use 'amplify codegen' to generate the local files

### Test

Test website with 'npm start'

When API schema has changed, you can regenerate local classes with 'amplify codegen'