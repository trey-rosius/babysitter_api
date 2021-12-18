from aws_lambda_powertools import Logger, Tracer
import boto3
import os

from entities.User import User
from entities.Job import Job

from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")

logger = Logger(service="jobs_applied_to")
tracer = Tracer()
table = dynamodb.Table(os.environ["TABLE_NAME"])


@tracer.capture_method
def jobsAppliedTo(username: str = ""):
    logger.debug(f'username is:{username}')

    try:
        response = table.query(
            IndexName="jobsAppliedTo",
            KeyConditionExpression='#gsi2pk = :gsi2pk',
            ExpressionAttributeNames={
                '#gsi2pk': 'GSI2PK'
            },
            ExpressionAttributeValues={
                ':gsi2pk': f'USER#{username}'
            },
            ScanIndexForward=False

        )

        user = User(response['Items'][0])
        logger.debug("jobs_applied_to {}".format(response["Items"]))

        jobs = [Job(item).job_dict() for item in response['Items'][1:]]

        return user.user_jobs(jobs)



    except ClientError as err:
        logger.debug(f"Error occured when getting applications per job{err.response['Error']}")
        raise err
