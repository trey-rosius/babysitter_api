Under Resources, let's create our cognito user pool and user pool client. We'll use AWS Cognito to
authenticate and secure our Graphql endpoints

```
  ###################
  # COGNITO POOLS
  ##################
  CognitoUserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub ${AWS::StackName}-UserPool
      AutoVerifiedAttributes:
        - email
  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: babysitter_api
      GenerateSecret: false
      UserPoolId: !Ref CognitoUserPool
      ExplicitAuthFlows:
        - ADMIN_NO_SRP_AUTH

```
Next, add the GraphQL API, API_KEY and GraphQl Schema

```
  ###################
  # GRAPHQL API
  ##################

  BabySitterApi:
    Type: "AWS::AppSync::GraphQLApi"
    Properties:
      Name: BabySitterApi
      AuthenticationType: "API_KEY"
      AdditionalAuthenticationProviders:
        - AuthenticationType: AMAZON_COGNITO_USER_POOLS
          UserPoolConfig:
            AwsRegion: !Ref AWS::Region
            UserPoolId: !Ref CognitoUserPool
      XrayEnabled: true
      LogConfig:
        CloudWatchLogsRoleArn: !GetAtt RoleAppSyncCloudWatch.Arn
        ExcludeVerboseContent: FALSE
        FieldLogLevel: ALL

  BabySitterApiKey:
    Type: AWS::AppSync::ApiKey
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId

  BabySitterApiSchema:
    Type: "AWS::AppSync::GraphQLSchema"
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId
      DefinitionS3Location: 'schema/schema.graphql'

```
We've set the default authentication type for our api to `API_KEY`. In our application, we have
one public endpoint(list) and we definitely have to control throttling for that endpoint.
<br />
This `API_KEY` is valid for 7 days after which it has to be regenerated again.
<br />

The next authentication type is `AMAZON_COGNITO_USER_POOLS` which requires a user to be authenticated before accessing the endpoint.
<br />

Then we have our graphQL schema in a file called `schema.graphql` located in the `schema` folder.
Here's the content of the file.
[GraphQl Schema](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/schema/schema.graphql)
<br />
Delete the hello world function and type in this one

```
  BabySitterFunction:
    Type: AWS::Serverless::Function # More info about Function Resource: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
    DependsOn:
      - LambdaLoggingPolicy
    Properties:
      CodeUri: babysitter/
      Handler: app.lambda_handler
      Role: !GetAtt AddBabysitterRole.Arn
      Runtime: python3.8
      Description: Sample Lambda Powertools Direct Lambda Resolver
      Tags:
        SOLUTION: LambdaPowertoolsPython

```
This function is our direct lambda resolver. It'll serve as the gateway to all the endpoints of our api.
We need permissions in-order to get tracer and logger functioning properly. That's why there's a
```
    DependsOn:
      - LambdaLoggingPolicy
```
Don't worry, we'll define the `LambdaLoggingPolicy` below.
<br />
This lambda function is called `app.py` and it's located in a folder called babysitter.
<br />

We also assign a role to the function, and this role has a set of policies attached to it.
This gives our lambda function permission to carryout a set of actions.
