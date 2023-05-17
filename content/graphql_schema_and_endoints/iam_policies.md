## AWS IAM (Identity and Access Management) Policies
When i started learning how to build serverless applications. I almost went nuts wrapping my head
head around AWS IAM.
<br />
A ton of serverless tutorials out there rarely talk about IAM and just dive into creating API's.
<br />
I think we should make a difference and cast some proper light on this concept.
<br />
#### What are IAM Policies
AWS services are born with zero permissions. You manage access in AWS by creating policies and attaching them to IAM identities (users, groups of users, or roles) or AWS resources.
<br />
<br />
A policy is an object in AWS that, when associated with an identity or resource, defines their permissions.
AWS evaluates these policies when an IAM principal (user or role) makes a request.
<br />
In simple terms,
> policies define authorizations to AWS services and resources.

<br />
There are different types of Policies.

Let's take a look at an **identity-based policy(IAM Policy)** from the api we are about to build.

```
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
              "dynamodb:Scan",
              "dynamodb:Query",
              "dynamodb:BatchGetItem",
              "dynamodb:DescribeTable"
              ]
            Resource:
              - !GetAtt DynamoDBHelloWorldTable.Arn
              - !Join [ '/',[!GetAtt DynamoDBHelloWorldTable.Arn,"index/*"]]
      Roles:
        - !Ref AddUserJobRole


```
This policy grants specific permissions to an AWS identity, thus giving them access to perform operations on
 an Amazon DynamoDB. Policies have a specific format.
<br />

Here's what you should take note of, in the above policy
- Type `AWS::IAM::Policy`
- PolicyName `DynamoDBReadPolicy`
- Statement Effect `Allow` explicitly allows the role access to the resource.
- Action represent  a set of functions a role can have on the resource.
- Resource represents the aws resource the above actions would be performed on.
In this case, it's our DynamoDB table and all it's respective Global Secondary Indexes.
- Roles: Attaching the above policy to a role(AWS Identity), grants them access to perform operations on
 said Resource(DynamoDB)
<br />
`!Ref` is a cloud formation intrinsic function that returns the value of the specified resource.
<br />

We create an `AssumeRolePolicyDocument` and attach it to our lambda function that'll define all the permissions
it requires for it's execution.
Remember that, it's the same role we've attached the DynamoDB policy to.
<br />

Therefore, once this role is attached to a lambda function, that function would have permissions to write to the
dynamoDB table.

```
  AddUserJobRole:
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

```
