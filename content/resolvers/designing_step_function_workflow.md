## Designing the step functions workflow
Here's how the final design looks like


![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/step_functions_workflow.png)

There are 2 ways to build a step functions workflow.

1) Using the ASL(Amazon States Language).
2) Using the AWS Step functions workflow visual design editor.

I recommend you go with option 2. The visual editor makes your life with step functions a lot easier.

If you are new to step functions or the visual editor, these are a couple of articles to get you up and running in no time.

- [Building Apps With Step Functions](https://phatrabbitapps.com/building-apps-with-step-functions)
- [The AWS Step Functions Workshop](https://catalog.workshops.aws/stepfunctions/en-US)

Let's get started.

Sign in to your AWS console, search, and open up step functions.

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

In the `API parameters` text area, add the following code to query Dynamodb.

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
For the table name, we used a variable, because we'll be dynamically adding that later through Infrastructure as Code.

We also use an intrinsic function `States.Format('JOB#{}',$.input.jobId)` to combine a string with the `jobId` variable.

If there are 20 applications for this job in DynamoDb, this query would return 21 items.

The Job plus the applications.

Navigate to the output tab and tick `Add Original input to output using ResultsPath.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/assets/output.png)

So in this step, the output would contain the original input we sent plus the list of items gotten from the query.
We'll pass this output as input to the next step.


## Step 2

Update Job Status from OPEN to CLOSED and application status for accepted applicant from PENDING to ACCEPTED.

We'll do this using a dynamo db transaction request.

Search and pull a `dynamodb transactwrite` items actions onto the canvas.

In the api parameters text area, add the following code block

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
We are performing 2 dynamodb update requests in a transaction. The only way the transaction succeeds is if both of the updates are successful. 

Which is what we want.  We don't want to accept a job application without closing the job or vice versa.

When the transaction request succeeds, it returns no output. So we want to take the input, which was the list of application items and job item, and then pass it on to the next state.

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
Put the rest of the job applications into an SQS queue, which would update the job application status from PENDING to DECLINED asynchronously.

In order to do this, we need to iterate through the list of applications. We'll use a map state for this. 

But remember that, the list of items contains all applications plus the Job. But we need to send only jobs into the queue.

And also, we shouldn't send the application item we had already accepted. 

We want to send only application items that would be declined.

So the first step is to use a pass state and filter off the job item.

## Step 3.1
Add a pass state to your canvas, navigate to the input tab, and tick `Transform input with Parameters - optional`

In the text area, add `"items.$": "$..getItems.Items[1:]"`.

This JsonPath filters off the first item from the `getItems.Items` list and creates a new list called `items`.

If you are wondering how we got `getItems.Items`, please check out the output from the transaction state.

## Step 3.2
Now that we have a list of all application items, iterate over them using a map state. 

Inside the map state, filter out the application we had already accepted using a choice state.

We do this, by comparing the application id of each item to the application id sent as input to the step functions. 

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

Here's the link to the complete step functions  workflow file [book_nanny.asl.json](https://github.com/trey-rosius/babysitter_api/blob/master/babysitter/step_functions_workflow/book_nanny.asl.json.)

At the SQS step, we added an ARN(Amazon resource name) for a queue, but didn't illustrate how we created that queue.
