from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from decimal import *
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

logger = Logger(service="create_job")
tracer = Tracer()

table = dynamodb.Table(os.environ["TABLE_NAME"])


# https://stackoverflow.com/questions/63026648/errormessage-class-decimal-inexact-class-decimal-rounded-while
@tracer.capture_method
def createJob(job: dict = {}):
    item = {
        "id": scalar_types_utils.make_id(),
        "jobType": job['jobType'],
        "username": job['username'],
        "startDate": scalar_types_utils.aws_date(),
        "endDate": scalar_types_utils.aws_date(),
        "startTime": scalar_types_utils.aws_time(),
        "endTime": scalar_types_utils.aws_time(),
        "jobStatus":job['jobStatus'],
        "longitude": Decimal(f"{job['longitude']}"),
        "latitude": Decimal(f"{job['latitude']}"),
        "address":job['address'],
        "city": job["city"],
        "cost": job["cost"],

    }

    logger.debug(f'job input :{item}')

    try:

        table.put_item(
            Item={
                "PK": f"USER#{item['username']}",
                "SK": f"JOB#{item['id']}",
                "GSI1PK": f"JOB#{item['id']}",
                "GSI1SK": f"JOB#{item['id']}",
                "GSI2SK": f"JOB#{item['id']}",
                **item
            }
        )

        return item



    except ClientError as err:
        logger.debug(f"Error occured during job creation {err.response['Error']}")
        raise err
