#### Roles and Policies.
Still under `Resource`, add these roles and policies.

```
  ###################
  # IAM PERMISSIONS AND ROLES
  ##################
  AppSyncServiceRole:
    Type: "AWS::IAM::Role"
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: "Allow"
            Principal:
              Service:
                - "appsync.amazonaws.com"
            Action:
              - "sts:AssumeRole"
  InvokeLambdaResolverPolicy:
    Type: "AWS::IAM::Policy"
    Properties:
      PolicyName: "DirectAppSyncLambda"
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: "Allow"
            Action: "lambda:invokeFunction"
            Resource:
              - !GetAtt BabySitterFunction.Arn
      Roles:
        - !Ref AppSyncServiceRole
  LambdaLoggingPolicy:
    Type: "AWS::IAM::Policy"
    Properties:
      PolicyName: LambdaXRayPolicy
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          -
            Effect: "Allow"
            Action: [
              "xray:PutTraceSegments",
              "xray:PutTelemetryRecords",
              "logs:CreateLogGroup",
              "logs:CreateLogStream",
              "logs:PutLogEvents"
              ]
            Resource: "*"
      Roles:
        - !Ref AddBabysitterRole
  DynamoDBReadPolicy:
    Type: "AWS::IAM::Policy"
    Properties:
      PolicyName: DynamoDBReadPolicy
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          -
            Effect: "Allow"
            Action: [
              "dynamodb:GetItem",
              "dynamodb:Query",

              ]
            Resource:
              - !GetAtt DynamoDBBabySitterTable.Arn
              - !Join [ '/',[!GetAtt DynamoDBBabySitterTable.Arn,"index/*"]]
      Roles:
        - !Ref AddBabysitterRole

  DynamoDBWritePolicy:
    Type: "AWS::IAM::Policy"
    Properties:
      PolicyName: DynamoDBWritePolicy
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          -
            Effect: "Allow"
            Action: [
              "dynamodb:PutItem",
              "dynamodb:UpdateItem",
              "dynamodb:ConditionCheckItem",
              "dynamodb:DeleteItem",
            ]
            Resource:
              - !GetAtt DynamoDBBabySitterTable.Arn
              - !Join [ '/',[!GetAtt DynamoDBBabySitterTable.Arn,"index/*"]]
      Roles:
        - !Ref AddBabysitterRole



  AddBabysitterRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Action:
            - "sts:AssumeRole"
            Effect: "Allow"
            Principal:
              Service:
                - "lambda.amazonaws.com"

  RoleAppSyncCloudWatch:
    Type: AWS::IAM::Role
    Properties:
      ManagedPolicyArns:
        - "arn:aws:iam::aws:policy/service-role/AWSAppSyncPushToCloudWatchLogs"
      AssumeRolePolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - sts:AssumeRole
            Principal:
              Service:
                - appsync.amazonaws.com

```