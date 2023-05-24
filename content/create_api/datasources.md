#### Datasource

The lambda function we created above would be used as the Datasource.Here's how we define it's `Resources`
```
  ###################
  # Lambda Direct Data Source and Resolver
  ##################
  BabySitterFunctionDataSource:
    Type: "AWS::AppSync::DataSource"
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId
      Name: "BabySitterLambdaDirectResolver"
      Type: "AWS_LAMBDA"
      ServiceRoleArn: !GetAtt AppSyncServiceRole.Arn
      LambdaConfig:
        LambdaFunctionArn: !GetAtt BabySitterFunction.Arn


```
The `ServiceRoleArn: !GetAtt AppSyncServiceRole.Arn` sets up a trust relationship between this datasource and appsync.
<br />

`LambdaFunctionArn: !GetAtt BabySitterFunction.Arn` points this datasource to the Lambda function we wish to use.
<br />

Before we begin creating resolvers, let's create the DynamoDb table.Still under `Resources`
```
 DynamoDBBabySitterTable:
    Type: AWS::DynamoDB::Table
    Properties:
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
        - AttributeName: GSI2PK
          AttributeType: S
        - AttributeName: GSI2SK
          AttributeType: S
        - AttributeName: jobStatus
          AttributeType: S
      BillingMode: PAY_PER_REQUEST
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: jobApplications
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: jobsAppliedTo
          KeySchema:
            - AttributeName: GSI2PK
              KeyType: HASH
            - AttributeName: GSI2SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: getJobsByStatus
          KeySchema:
            - AttributeName: jobStatus
              KeyType: HASH
            - AttributeName: SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

```
I already explained why we need Global Secondary Indexes, and why our table is structured this way. Short answer is,
`access patterns`
