
## Adding State Machine resource to template.yaml

In this step, we have to add the state machine resource plus all variables and permissions to template.yaml.

```

  BookNannyStateMachine:
    Type: AWS::Serverless::StateMachine # More info about State Machine Resource: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-statemachine.html
    Properties:
      DefinitionUri: babysitter/step_functions_workflow/book_nanny.asl.json
      DefinitionSubstitutions:
        DDBTable: !Ref DynamoDBBabySitterTable
        SQSURL: !Ref UpdateJobApplicationsSQSQueue

      Policies: # Find out more about SAM policy templates: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html
        - DynamoDBWritePolicy:
            TableName: !Ref DynamoDBBabySitterTable
        - DynamoDBReadPolicy:
            TableName: !Ref DynamoDBBabySitterTable
        - SQSSendMessagePolicy:
            QueueName: !GetAtt UpdateJobApplicationsSQSQueue.Arn


```

We point the `DefinitionUri` to the `step_functions_workflow.asl.json` file.
 and substitute the DynamoDB and SQS variables with those in our application. 

Give permissions to the state machine to access the dynamodb and SQS queues.
