#### Booking a nanny
In this section, we'll be using [Amazon Simple Queue Service (SQS)](https://aws.amazon.com/sqs/) to decouple and scale our application.
<br />

[Amazon Simple Queue Service (SQS)](https://aws.amazon.com/sqs/) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.
<br />

Using SQS, you can send, store, and receive messages between software components at any volume, without losing messages or requiring other services to be available
<br />

Read more about Amazon SQS from the official website above.
<br />

When a parent creates a job, nannies can apply for that job. The parent would then be able to accept the application
for whoever they see fit for the job.

<br />

Booking a nanny entails, firstly, accepting the nanny's job application(changing application status), declining all other job applications, so that
the other applicants know they weren't selected, and then closing the job, so that it won't be available anymore for applying to.
<br />

Here's a breakdown of how our code would work
- Get all applications for a job.
- Update Job Status from OPEN to CLOSED and application status for accepted applicant from PENDING to ACCEPTED
- Put the rest of the job applications into an SQS queue, which would update the job application status from
PENDING to DECLINED asynchronously.
<br />

For added functionality, it'll be good to send a push notification and an email to the applicant whose application was
`accepted`. But this functionality isn't within the scope of this tutorial.
<br />

Let's get started.
<br />

In Iac(Infrastructure as Code), the first step is to create/configure a SQS Queue and a Dead Letter queue  like so

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

We set `maxReceiveCount` to 5, to recieve 5 messages at a time.

Next, we have to write a function, based on the breakdown we outlined above,
Here's how the code looks like.
You can find it in `resolvers/jobs/book_nanny.py`

```

from aws_lambda_powertools import Logger, Tracer
import boto3
import os
import json

from boto3.dynamodb.conditions import Key

from decima_encoder import handle_decimal_type

from botocore.exceptions import ClientError

logger = Logger(service="book_nanny")
tracer = Tracer(service="book_nanny")
# client library
client = boto3.client('dynamodb')
# resource library
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
sqs = boto3.resource("sqs")
queue = sqs.Queue(os.environ["UPDATE_JOB_APPLICATIONS_SQS_QUEUE"])


def book_nanny(username: str = "", jobId: str = "", applicationId: str = "", applicationStatus: str = ""):
    logger.info({f"Parameters {jobId, applicationId, applicationStatus}"})
    # first step involves getting all applications for  the said job
    response_items = table.query(
        IndexName="jobApplications",
        KeyConditionExpression=Key('GSI1PK').eq(f'JOB#{jobId}'),
        ScanIndexForward=False

    )
    logger.info(f'response is {response_items["Items"]}')

    logger.debug({"application response is": response_items['Items'][1:]})
    try:

        response = client.transact_write_items(
            TransactItems=[{
                'Update': {
                    'TableName': os.environ["TABLE_NAME"],
                    "Key": {
                        "PK": {
                            "S": f'USER#{username}'
                        },
                        "SK": {
                            "S": f'JOB#{jobId}'
                        },
                    },
                    "ConditionExpression": "username = :username",
                    "UpdateExpression": "SET jobStatus = :jobStatus",
                    "ExpressionAttributeValues": {
                        ":username": {'S': username},
                        ":jobStatus": {'S': 'CLOSED'}
                    },
                    'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                }

            }, {
                'Update': {
                    'TableName': os.environ["TABLE_NAME"],
                    "Key": {
                        "PK": {
                            "S": f"JOB#{jobId}#APPLICATION#{applicationId}"
                        },
                        "SK": {
                            "S": f"JOB#{jobId}#APPLICATION#{applicationId}"
                        },
                    },
                    "UpdateExpression": "SET jobApplicationStatus= :jobApplicationStatus",
                    "ExpressionAttributeValues": {
                        ":jobApplicationStatus": {'S': applicationStatus},

                    },
                    'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                }
            }],
            ReturnConsumedCapacity='TOTAL',
            ReturnItemCollectionMetrics='SIZE'
        )
        logger.debug(f'transaction response is {response}')
        '''
        create a for loop and send all queue messages
        '''
        for item in response_items['Items'][1:]:
            logger.debug('sending messages to sqs {}'.format(json.dumps(item, default=handle_decimal_type)))
            if item['id'] != applicationId:
                queue.send_message(MessageBody=json.dumps(item, default=handle_decimal_type))
            else:
                logger.info("Accepted applicationId. So we don't have to put it into SQS")
                # you can send a notification or an email to the accepted user here

        return True

    except ClientError as err:
        logger.debug(f"Error occurred during transact write{err.response}")
        logger.debug(f"Error occurred during transact write{err}")
        logger.debug(f"Error occurred during transact write{err.response['Error']}")
        if err.response['Error']['Code'] == 'TransactionCanceledException':
            if err.response['CancellationReasons'][0]['Code'] == 'ConditionalCheckFailed':
                errObj = Exception("You aren't authorized to make this update")

                raise errObj

        else:
            raise err


```

<br />

So, the code simply does this.

- Get all applications for a job.
- Update Job Status from OPEN to CLOSED and application status for accepted applicant from PENDING to ACCEPTED
- Put the rest of the job applications into an SQS queue, which would update the job application status from
PENDING to DECLINED asynchronously.
<br />

We expect a function to receive all these messages from the SQS queue and process them.
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
Since our function would be performing an update operation on dynamoDB items, it's just right we assign
dynamoDB update permissions to it.
<br />

Our function would poll SQS messages in batches of 5 (`BatchSize: 5`)
<br />

Since we are using SQS,we must configure our Lambda function event source to use `ReportBatchItemFailures`.
<br />

Remember that our lambda function is triggered with a batch of messages.
<br />

If our function fails to process any message from the batch, the entire batch returns to our queue. This same batch is then retried until either condition happens first:
a) your Lambda function returns a successful response
b) record reaches maximum retry attempts, or
c) when records expire

<br />
We would use the `batch processing` utility of the `aws-lambda-powertools` to ensure that, batch records are processed individually – only messages that failed to be processed return to the queue  for a further retry.
<br />

This works when two mechanisms are in place:
<br />

- `ReportBatchItemFailures` is set in your SQS event source properties
- A [specific response](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#sqs-batchfailurereporting-syntax) is returned so Lambda knows which records should not be deleted during partial responses.

<br />

Create a file called `update_job_application.py` in the `/babysitter` directory type in the following code

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
1) Instantiate our dynamoDB resource, and also the BatchProcessor and choose EventType.SQS for the event type.
2) Define the function to handle each batch record, and use SQSRecord type annotation for autocompletion.
In our case, we updated each `jobApplicationStatus` to `DECLINED`
3) We use `batch_processor` decorator to kick off processing.
4) Return the appropriate response contract to Lambda via .response() processor method
