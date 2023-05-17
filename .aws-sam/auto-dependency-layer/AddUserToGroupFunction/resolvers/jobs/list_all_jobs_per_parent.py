from aws_lambda_powertools import Logger, Tracer
import boto3
import os

from entities.user_entity import UserEntity
from entities.job_entity import JobEntity


from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
logger = Logger(service="sample_resolver")

table = dynamodb.Table(os.environ["TABLE_NAME"])


def list_all_jobs_per_parent(username: str = "", userType: str = ""):
    logger.debug(f"username and type are:{username},{userType}")
    # add another condition to ensure that only nannies and admins can query jobs. Use the userType attribute

    try:
        response = table.query(
            KeyConditionExpression="#pk = :pk",
            ExpressionAttributeNames={"#pk": "PK"},
            ExpressionAttributeValues={":pk": f"USER#{username}"},
            ScanIndexForward=False,
        )

        user = UserEntity(response["Items"][0])

        jobs = [JobEntity(item).job_dict() for item in response["Items"][1:]]

        return user.user_jobs(jobs)

    except ClientError as err:
        logger.debug(
            f"Error occured when getting applications per job{err.response['Error']}"
        )
        raise err
