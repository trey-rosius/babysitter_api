#### Create Job Endpoint
This endpoint is reserved for PARENTS only.It allows parents to put up job offers, which can be applied to
by nanny's.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/post.png)
Here's how the schema looks like
```

            createJob(job:CreateJobInput!):Job!
            @aws_cognito_user_pools(cognito_groups: ["parent"])

```
It takes as input, a couple of attributes alongside, the start and end dates, the address and geographical location(longitude and latitude),
the cost, and also, if the job requires the nanny to come in daily, or stay in.
<br />
**Endpoint**
- PK= `USER#<Username>`
- SK= `JOB#<JobId>`

1) Create file called `create.py` in the directory `babysitter/resolvers/jobs/` and type in the following code
```
from aws_lambda_powertools import Logger, Tracer
import boto3
import os

from decimal import *
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

logger = Logger(service="create_job")
tracer = Tracer(service="create_job")

table = dynamodb.Table(os.environ["TABLE_NAME"])


# https://stackoverflow.com/questions/63026648/errormessage-class-decimal-inexact-class-decimal-rounded-while
@tracer.capture_method
def createJob(job=None):
    if job is None:
        job = {}
    item = {
        "id": scalar_types_utils.make_id(),
        "jobType": job['jobType'],
        "username": job['username'],
        "startDate": scalar_types_utils.aws_date(),
        "endDate": scalar_types_utils.aws_date(),
        "startTime": scalar_types_utils.aws_time(),
        "endTime": scalar_types_utils.aws_time(),
        "jobStatus": job['jobStatus'],
        "longitude": Decimal(f"{job['longitude']}"),
        "latitude": Decimal(f"{job['latitude']}"),
        "address": job['address'],
        "city": job["city"],
        "cost": job["cost"],

    }

    logger.debug(f'job input :{item}')

    try:

        response = table.put_item(
            Item={
                "PK": f"USER#{item['username']}",
                "SK": f"JOB#{item['id']}",
                "GSI1PK": f"JOB#{item['id']}",
                "GSI1SK": f"JOB#{item['id']}",
                "GSI2SK": f"JOB#{item['id']}",
                **item
            }
        )

        logger.info(" create job item response {}".format(response))
        return item



    except ClientError as err:
        logger.debug(f"Error occurred during job creation {err.response['Error']}")
        raise err


```
The `create_job` method receives a job dictionary, containing job attributes and puts them into our
dynamodb table.
<br />

2) Create a file called `job.py` in the directory `babysitter/resolvers` and add the create job
endpoint. This file would contain all job endpoints.


```
from decimal import Decimal
from typing import Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from resolvers.jobs.create_job import create_job as createJob



logger = Logger(child=True)
router = Router()


@router.resolver(type_name="Mutation", field_name="createJob")
def create_job(job=None) -> Dict[str, Decimal]:
    if job is None:
        job = {}
    return createJob(job)

```

Take note of the resolvers `type_name` and `field_name`.

3) Add `create_job` Resolver to Resources in template.yml
```
  CreeateJobResolver:
    Type: "AWS::AppSync::Resolver"
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId
      TypeName: "Mutation"
      FieldName: "createJob"
      DataSourceName: !GetAtt BabySitterFunctionDataSource.Name


```
