#### Booking a nanny
In this section, we'll be using [AWS Step Functions](https://aws.amazon.com/step-functions/) to orchestrate the booking process and  [Amazon Simple Queue Service (SQS)](https://aws.amazon.com/sqs/) to decouple and scale the application.
<br />

AWS Step Functions is a low code visual workflow service that orchestrates other AWS services and supports common workflow patterns that simplify the implementation of common tasks so developers can focus on higher-value business logic.

Here's a great step functions article to get you started [Building Apps With Step Functions](https://phatrabbitapps.com/building-apps-with-step-functions).

Amazon SQS is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.
<br />


Using SQS, you can send, store, and receive messages between AWS Services at any volume, without losing messages or requiring other services to be available
<br />

Read more about Amazon SQS from the official website above.
<br />

Before we proceed, here's a recap on how this endpoint was written before

> The first version of the api didn't use step functions for the booking process.
> Everything was done with custom code in a lambda function.
>
>After reviewing the api 2 yrs later, I decided to
> refactor the lambda function code into a step functions workflow.
>
>Choosing automation over custom logic.
>
>This led to a huge performance boost.
>
> As a matter of fact, the workflow took half the time the lambda function took to do the job.
>
Here's the full conversation on linked
[Performance Results Are In](https://www.linkedin.com/feed/update/urn:li:activity:7066700086679863296/?commentUrn=urn%3Ali%3Acomment%3A(activity%3A7066700086679863296%2C7066766726595559424)&dashCommentUrn=urn%3Ali%3Afsd_comment%3A(7066766726595559424%2Curn%3Ali%3Aactivity%3A7066700086679863296)&dashReplyUrn=urn%3Ali%3Afsd_comment%3A(7067120504096051201%2Curn%3Ali%3Aactivity%3A7066700086679863296)&replyUrn=urn%3Ali%3Acomment%3A(activity%3A7066700086679863296%2C7067120504096051201))

I used vegeta to run 50 transactions per second for 60 seconds on both the lambda function code and the refactored express step functions workflow.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/performance.png)


Let's Proceed.

When a parent creates a job, nannies can apply for that job. The parent would then be able to accept(book a nanny) the application
for whomever they see fit for the job.

<br />

Booking a nanny entails,
- Getting all applications for the job in particular.
- accepting one of the job application(changing application status),
- declining all other job applications,
- closing the job, so that it won't be available anymore for applying to.
<br />

Here's a breakdown of how our code would work
- Get all applications for a job with a dynamodb Query and GSI.
- Update Job Status from OPEN to CLOSED and application status for accepted applicant from PENDING to ACCEPTED
- Put the rest of the job applications into an SQS queue, which would update the job application status from
PENDING to DECLINED asynchronously.
<br />

This is primary candidate for a step functions workflow.We'll use an Express workflow, since our
use case would be short-lived and instantaneous.

For added functionality, it'll be good to send a push notification and an email to the applicant whose application was
`accepted`. But this functionality isn't within the scope of this tutorial.
<br />

Let's get started.
<br />

## Designing the step functions workflow
Here's how the final design looks like


![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/step_functions_workflow.png)

There are 2 ways to build a step functions workflow.
1) Using the ASL(Amazon States Language)
2) Using the AWS Step functions workflow visual design editor.

I recommend you go with 2. The visual editor makes your life with step functions a lot easier.

If you are new to step functions or the visual editor, these are a couple of articles to get you
up and running in no time.

- [Building Apps With Step Functions](https://phatrabbitapps.com/building-apps-with-step-functions)
- [The AWS Step Functions Workshop](https://catalog.workshops.aws/stepfunctions/en-US)

Let's get started.

Sign in to your aws console, search and open up step functions.

Click on the rectangular orange button which says `create state machine`

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/create_sf.png)

Select express step functions and click next.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/select_sf_type.png)

The first step is to query all applications for a particular job using the `jobApplications` GSI.

On the visual editor, search for dynamodb query and pull it onto the canvas.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/add_query.png)

In the `API paramter` text area, add the following code to query dynamodb.

```
{
  "TableName": "${DDBTable}",
  "IndexName": "jobApplications",
  "ScanIndexForward": "False",
  "KeyConditionExpression": "GSI1PK = :GSI1PK",
  "ExpressionAttributeValues": {
    ":GSI1PK": {
      "S.$": "States.Format('JOB#{}',$.input.jobId)"
    }
  },
  "ReturnConsumedCapacity": "TOTAL"
}

```
For the table name, we used a variable, because we'll be dynamically adding that later, through Infrastructure as Code.

We also use an intrinsic function `States.Format('JOB#{}',$.input.jobId)` to combine a string with the jobId.

If there are 20 applications for this job in DynamoDb, this query would return 21 items.

The Job plus the applications.

Navigate to the output tab


```
  "Get All Job Applications": {
      "Type": "Task",
      "Parameters": {
        "TableName": "${DDBTable}",
        "IndexName": "jobApplications",
        "ScanIndexForward": "False",
        "KeyConditionExpression": "GSI1PK = :GSI1PK",
        "ExpressionAttributeValues": {
          ":GSI1PK": {
            "S.$": "States.Format('JOB#{}',$.input.jobId)"
          }
        },
        "ReturnConsumedCapacity": "TOTAL"
      },
      "Resource": "arn:aws:states:::aws-sdk:dynamodb:query",
      "Next": "TransactWriteItems",
      "ResultPath": "$.getItems"
    },
```


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

We set `maxReceiveCount` to 5, to receive 5 messages at a time.

Next, open up
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
