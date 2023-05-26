## Create SQS Queue
So let's create the queue now.

We have to create/configure a SQS Queue and a Dead Letter queue. Let's do that in `template.yaml`

```
  ###################
   #   SQS
  ###################
  UpdateJobApplicationsSQSQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 20
      RedrivePolicy:
        deadLetterTargetArn:
          !GetAtt UpdateJobApplicationsSQSDLQ.Arn
        maxReceiveCount: 5
  UpdateJobApplicationsSQSDLQ:
    Type: AWS::SQS::Queue


```

The name of our SQS queue is `UpdateJobApplicationsSQSQueue`.
<br />

To prevent other consumers from processing the message again, Amazon SQS sets a visibility timeout, a period of time during which Amazon SQS prevents other consumers from receiving and processing the message
<br />

Here, we set the `VisibilityTimeout` to 20 seconds.
<br />

Dead Letter Queues (DLQ) are source queues for messages that couldn't be processed for some reason.
If you want to re-process all messages in DLQ, that's where the `RedrivePolicy` comes in.
<br />

We set `maxReceiveCount` to 5, to receive 5 messages at a time.

We expect a function to receive all these messages from the SQS queue and process them.
Process them, meaning change the status of the application from `PENDING` to `DECLINED.

Let's configure this function in `template.yaml`
<br />

```

  UpdateJobApplicationsFunction:
    Type: AWS::Serverless::Function
    DependsOn:
      - LambdaLoggingPolicy
    Properties:
      CodeUri: babysitter/
      Handler: update_job_application.lambda_handler
      Runtime: python3.8
      Description:  Lambda Powertools Direct Lambda Resolver
      Policies:
        - SQSPollerPolicy:
            QueueName:
              !GetAtt UpdateJobApplicationsSQSQueue.QueueName
        - Statement:

            - Effect: Allow
              Action:
                - "dynamodb:UpdateItem"
              Resource:

                - !GetAtt DynamoDBBabySitterTable.Arn

      Events:
        RetrieveFromSQS:
          Type: SQS
          Properties:
            Queue: !GetAtt UpdateJobApplicationsSQSQueue.Arn
            BatchSize: 5
            FunctionResponseTypes:
              - ReportBatchItemFailures


```
`SQSPollerPolicy` gives permission to `UpdateJobApplicationsFunction` to poll our SQS queue.
<br />
Since our function would be performing an update operation on Dynamo db items, it's just right we assign Dynamo db update permissions to it.
<br />

Our function would poll SQS messages in batches of 5 (`BatchSize: 5`)
<br />

Since we are using SQS, we must configure our Lambda function event source to use `ReportBatchItemFailures`.
<br />

Remember that our lambda function is triggered with a batch of messages.
<br />

If the function fails to process any message from the batch, the entire batch returns to the queue. This same batch is then retried until either condition happens first:

a) your Lambda function returns a successful response
b) record reaches maximum retry attempts, or
c) records expire

<br />
We would use the `batch processing` utility of the `aws-lambda-powertools` to ensure that, batch records are processed individually. Only messages that failed to be processed return to the queue for a further retry.
<br />

This works when two mechanisms are in place:
<br />

- `ReportBatchItemFailures` is set in your SQS event source properties
- A [specific response](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#sqs-batchfailurereporting-syntax) is returned so Lambda knows which records should not be deleted during partial responses.

<br />

Create a file called `update_job_application.py` in the `/babysitter` directory and type in the following code

```

import json
import os
import boto3
from typing import Any, List, Literal, Union
from aws_lambda_powertools.utilities.batch import (BatchProcessor,
                                                   EventType,
                                                   FailureResponse,
                                                   SuccessResponse,
                                                   batch_processor)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer(service="update_job_application")
logger = Logger(service="update_job_application")


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
processor = BatchProcessor(event_type=EventType.SQS)

@tracer.capture_method
def record_handler(record: SQSRecord):
    """
    Handle messages from SQS Queue containing job applications.
    Update each job application status to DECLINED
    """
    payload:str = record.body

    logger.info(f"payload has {len(payload)} records")

    if payload:
        logger.debug(" application item is {}".format(payload))
        item = json.loads(payload)
        response = table.update_item(
            Key={
                'PK': f"JOB#{item['jobId']}#APPLICATION#{item['id']}",
                'SK': f"JOB#{item['jobId']}#APPLICATION#{item['id']}"
            },
            ConditionExpression="attribute_exists(PK)",
            UpdateExpression="set jobApplicationStatus= :jobApplicationStatus",

            ExpressionAttributeValues={
                ':jobApplicationStatus': 'DECLINED'
            },
            ReturnValues="ALL_NEW"
        )

        logger.debug({' update response': response['Attributes']})



@logger.inject_lambda_context
@tracer.capture_lambda_handler
@batch_processor(record_handler=record_handler, processor=processor)
def lambda_handler(event, context: LambdaContext):
    batch = event["Records"]
    with processor(records=batch, processor=processor):
        processed_messages: List[Union[SuccessResponse, FailureResponse]] = processor.process()

    for messages in processed_messages:
        for message in messages:
            status: Union[Literal["success"], Literal["fail"]] = message[0]
            result: Any = message[1]
            record: SQSRecord = message[2]
            logger.debug("status is {}".format(status))
            logger.debug("result is {}".format(result))
            logger.debug("record is {}".format(record))
    return processor.response()


```
Here are the steps involved in processing messages from our SQS in the above code.

1) Instantiate a dynamoDB resource, a `BatchProcessor`, and choose `EventType.SQS` for the event type.
2) Define the function to handle each batch record, and use SQSRecord type annotation for autocompletion.
In our case, we updated each application item's `jobApplicationStatus` field to `DECLINED`
3) We use `batch_processor` decorator to kick off processing.
4) Return the appropriate response contract to Lambda via .response() processor method
