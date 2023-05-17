from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

logger = Logger(service="apply_to_job")
tracer = Tracer(service="apply_to_job")

table = dynamodb.Table(os.environ["TABLE_NAME"])


# https://stackoverflow.com/questions/63026648/errormessage-class-decimal-inexact-class-decimal-rounded-while
@tracer.capture_method
def apply_to_job(application: dict = {}):
    item = {
        "id": scalar_types_utils.make_id(),
        "jobId": application["jobId"],
        "username": application["username"],
        "jobApplicationStatus": application["jobApplicationStatus"],
        "createdOn": scalar_types_utils.aws_timestamp(),
    }

    logger.debug(f"job application input :{item}")

    try:

        table.put_item(
            Item={
                "PK": f"JOB#{item['jobId']}#APPLICATION#{item['id']}",
                "SK": f"JOB#{item['jobId']}#APPLICATION#{item['id']}",
                "GSI1PK": f"JOB#{item['jobId']}",
                "GSI1SK": f"APPLICATION#{item['id']}",
                "GSI2PK": f"USER#{item['username']}",
                "GSI2SK": f"JOB#{item['jobId']}",
                **item,
            }
        )

        return item

    except ClientError as err:
        logger.debug(f"Error occurred during job creation {err.response['Error']}")
        raise err
