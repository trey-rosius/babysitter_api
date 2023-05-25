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

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master//assets/create_sf.png)

Select express step functions and click next.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master//assets/select_sf_type.png)

## Step 1
Here's the input to the step functions workflow

```json
{
  "input": {
    "username": "ro",
    "jobId": "5b56e557-5f2a-4fbd-8a07-35bce9b6163a",
    "applicationId": "3d859e26-d7ce-4208-a60a-3793e4869a22",
    "applicationStatus": "ACCEPTED"
  }
}
```
- It has the `jobId` of the job we have to get applications for.
- `applicationId` of the application we would accept for the job.
- `applicationStatus` of the application.

This input would remain in the context object of the step functions execution and we 
can access it at any moment within the execution using `$$`.

Let's proceed. 

Query all applications for a particular job using the `jobApplications` GSI.

On the visual editor, search for dynamodb query and pull it onto the canvas.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/add_query.png)

In the `API parameters` text area, add the following code to query dynamodb.

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

Navigate to the output tab and tick `Add Original input to output using ResultsPath.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/output.png)


## Step 2

Update Job Status from OPEN to CLOSED and application status for accepted applicant from PENDING to ACCEPTED.

We'll do this using a transaction request.

Search and pull a dynamodb transactwrite items actions onto the canvas.

In the api parameters text area, add in the following code block

```
{
  "TransactItems": [
    {
      "Update": {
        "TableName": "${DDBTable}",
        "Key": {
          "PK": {
            "S.$": "States.Format('USER#{}',$.input.username)"
          },
          "SK": {
            "S.$": "States.Format('JOB#{}',$.input.jobId)"
          }
        },
        "ConditionExpression": "username = :username",
        "UpdateExpression": "SET jobStatus = :jobStatus",
        "ExpressionAttributeValues": {
          ":username": {
            "S.$": "$.input.username"
          },
          ":jobStatus": {
            "S": "CLOSED"
          }
        },
        "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
      }
    },
    {
      "Update": {
        "TableName": "${DDBTable}",
        "Key": {
          "PK": {
            "S.$": "States.Format('JOB#{}APPLICATION#{}',$.input.jobId,$.input.applicationId)"
          },
          "SK": {
            "S.$": "States.Format('JOB#{}APPLICATION#{}',$.input.jobId,$.input.applicationId)"
          }
        },
        "UpdateExpression": "SET jobApplicationStatus= :jobApplicationStatus",
        "ExpressionAttributeValues": {
          ":jobApplicationStatus": {
            "S.$": "$.input.applicationStatus"
          }
        },
        "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
      }
    }
  ]
}
```
We are performing 2 dynamo update requests in a transaction. The only way the transaction succeeds is,
if both of the updates are successful. Which is the right use-case we want. We don't want to Accept a job application
without closing the job or vice versa.

When the transaction request succeeds, it returns no output. So we want to take the input, which was the 
list of application items and job, and then pass it onto the next state.

In the output tab, choose `Add original input to output using ResultPath - optional  Info`, then from the dropdown menu,
select `Discard results and keep original input`.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/transact.png)

Here's the output from this step 

```json
{
  "name": "TransactWriteItems",
  "output": {
    "input": {
      "username": "ro",
      "jobId": "5b56e557-5f2a-4fbd-8a07-35bce9b6163a",
      "applicationId": "3d859e26-d7ce-4208-a60a-3793e4869a22",
      "applicationStatus": "ACCEPTED"
    },
    "getItems": {
      "ConsumedCapacity": {
        "CapacityUnits": 0.5,
        "TableName": "babysitter-api-DynamoDBBabySitterTable-L4IC34BCHP6D"
      },
      "Count": 4,
      "Items": [
        {
          "jobStatus": {
            "S": "CLOSED"
          },
          "address": {
            "S": "Douala, makepe"
          },
          "cost": {
            "N": "10"
          },
          "endDate": {
            "S": "2023-05-19Z"
          },
          "city": {
            "S": "Douala"
          },
          "latitude": {
            "N": "234423123"
          },
          "GSI1PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI2SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "startTime": {
            "S": "19:04:16.469Z"
          },
          "endTime": {
            "S": "19:04:16.469Z"
          },
          "id": {
            "S": "5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "PK": {
            "S": "USER#ro"
          },
          "jobType": {
            "S": "BABYSITTING"
          },
          "startDate": {
            "S": "2023-05-19Z"
          },
          "longitude": {
            "N": "1.5432342345"
          },
          "username": {
            "S": "ro"
          }
        },
        {
          "jobId": {
            "S": "5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "jobApplicationStatus": {
            "S": "PENDING"
          },
          "GSI2SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1SK": {
            "S": "APPLICATION#3d859e26-d7ce-4208-a60a-3793e4869a22"
          },
          "SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a#APPLICATION#3d859e26-d7ce-4208-a60a-3793e4869a22"
          },
          "GSI2PK": {
            "S": "USER#stark"
          },
          "id": {
            "S": "3d859e26-d7ce-4208-a60a-3793e4869a22"
          },
          "PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a#APPLICATION#3d859e26-d7ce-4208-a60a-3793e4869a22"
          },
          "createdOn": {
            "N": "1684523887"
          },
          "username": {
            "S": "stark"
          }
        },
        {
          "jobId": {
            "S": "5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "jobApplicationStatus": {
            "S": "DECLINED"
          },
          "GSI2SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1SK": {
            "S": "APPLICATION#31aff80e-a2b1-431e-b5af-5362b27e5ca5"
          },
          "SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a#APPLICATION#31aff80e-a2b1-431e-b5af-5362b27e5ca5"
          },
          "GSI2PK": {
            "S": "USER#ro"
          },
          "id": {
            "S": "31aff80e-a2b1-431e-b5af-5362b27e5ca5"
          },
          "PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a#APPLICATION#31aff80e-a2b1-431e-b5af-5362b27e5ca5"
          },
          "createdOn": {
            "N": "1684523858"
          },
          "username": {
            "S": "ro"
          }
        },
        {
          "jobId": {
            "S": "5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "jobApplicationStatus": {
            "S": "DECLINED"
          },
          "GSI2SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a"
          },
          "GSI1SK": {
            "S": "APPLICATION#1d902eb8-b8e5-4fde-a086-ad830f1f7143"
          },
          "SK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a#APPLICATION#1d902eb8-b8e5-4fde-a086-ad830f1f7143"
          },
          "GSI2PK": {
            "S": "USER#steve"
          },
          "id": {
            "S": "1d902eb8-b8e5-4fde-a086-ad830f1f7143"
          },
          "PK": {
            "S": "JOB#5b56e557-5f2a-4fbd-8a07-35bce9b6163a#APPLICATION#1d902eb8-b8e5-4fde-a086-ad830f1f7143"
          },
          "createdOn": {
            "N": "1684523539"
          },
          "username": {
            "S": "steve"
          }
        }
      ],
      "ScannedCount": 4
    }
  },
  "outputDetails": {
    "truncated": false
  }
}
```
## Step 3
Put the rest of the job applications into an SQS queue, which would update the job application status from
PENDING to DECLINED asynchronously.

In-order to do this, we need to iterate through the list of applications. We'll use a map state
for this. 

But remember that, the list of items contains all applications plus the Job.But we need to send only jobs into the queue.

And also, we shouldn't send the application we had already accepted. 

We want to send only applications that would be declined.

So the first step is to use a pass state and filter off the job item.
## Step 3.1
Add a pass state to your canvas , navigate to the input tab and tick `Transform input with Parameters - optional`

In the text area, add `"items.$": "$..getItems.Items[1:]"`.

This JsonPath filters off the first item from the `getItems.Items` list and creates new list called `items`.

If you are wondering how we got `getItems.Items` , please check out the output from the transaction state.

## Step 3.2
Now that we have a list of all application items, we need to iterate over them using map state.

Inside the map state, we need to filter out the application we had already accepted.

We do this, by comparing the application id of each item to the application id sent from the input step at 
the start of the step functions workflow. 

You might be wondering how we get the inputs sent from the start of the workflow. 

The input is available in an `Execution.Input` object in the step functions context object. 

```json
{
    "Execution": {
        "Id": "String",
        "Input": {},
        "Name": "String",
        "RoleArn": "String",
        "StartTime": "Format: ISO 8601"
    },
    "State": {
        "EnteredTime": "Format: ISO 8601",
        "Name": "String",
        "RetryCount": Number
    },
    "StateMachine": {
        "Id": "String",
        "Name": "String"
    },
    "Task": {
        "Token": "String"
    }
}
```
Therefore, accessing the `applicationId` would be `"$$.Execution.Input.input.applicationId"`

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/map.png)

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/choice.png)

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/sqs.png)

Here's the link to the complete `asl.json` step functions file [book_nanny.asl.json](https://github.com/trey-rosius/babysitter_api/blob/master/babysitter/step_functions_workflow/book_nanny.asl.json.)

At the SQS step, we added an ARN(Amazon resource name) for a queue, but didn't illustrate how we created that queue.

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
In our case, we updated each application item's `jobApplicationStatus` field to `DECLINED`
3) We use `batch_processor` decorator to kick off processing.
4) Return the appropriate response contract to Lambda via .response() processor method

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

We substitute the dynamodb and sqs variables with those in our application. 

And also give permissions to our state machine to access dynamodb and sqs queues.
