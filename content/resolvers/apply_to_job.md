#### Apply to Job
After viewing a list of available jobs, the next step is applying to that job.This endpoint is 
reserved for nannies only.
```
applyToJob(application:CreateJobApplicationInput!):JobApplication!
@aws_cognito_user_pools(cognito_groups: ["nanny"])


```

The PK and SK for this endpoint are
```
PK= JOB#<JobId>#APPLICATION#<applicationId>
SK = JOB#<JobId>#APPLICATION#<applicationId>

```

Here's the complete code 
```
from aws_lambda_powertools import Logger,Tracer
import boto3
import os
from decimal import *
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

logger = Logger(service="apply_to_job")
tracer = Tracer()

table = dynamodb.Table(os.environ["TABLE_NAME"])


# https://stackoverflow.com/questions/63026648/errormessage-class-decimal-inexact-class-decimal-rounded-while
@tracer.capture_method
def applyToJob(application: dict = {}):
    item = {
        "id": scalar_types_utils.make_id(),
        "jobId": application['jobId'],
        "username": application['username'],
        "jobApplicationStatus":application['jobApplicationStatus'],
        "createdOn":scalar_types_utils.aws_timestamp()

    }

    logger.debug(f'job application input :{item}')

    try:

        table.put_item(
            Item={
                "PK": f"JOB#{item['jobId']}#APPLICATION#{item['id']}",
                "SK": f"JOB#{item['jobId']}#APPLICATION#{item['id']}",
                "GSI1PK": f"JOB#{item['jobId']}",
                "GSI1SK": f"APPLICATION#{item['id']}",
                "GSI2PK": f"USER#{item['username']}",
                "GSI2SK": f"JOB#{item['jobId']}",
                **item
            }
        )

        return item



    except ClientError as err:
        logger.debug(f"Error occured during job creation {err.response['Error']}")
        raise err


```
<br />

At this point, we are simply repeating steps over and over and over again and i know it's getting boring.
<br />
Let's look at one of the most important features of the app and close this series.
