from aws_lambda_powertools import Logger, Tracer
import boto3
import os
import json
import decimal
from entities.User import User
from entities.Job import Job
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from boto3.dynamodb.conditions import Key

from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
logger = Logger(service="sample_resolver")

table = dynamodb.Table(os.environ["TABLE_NAME"])


def listAllJobsPerParent(username: str = "", userType: str = ""):
    logger.debug(f'username and type are:{username},{userType}')
    # add another condition to ensure that only nannies and admins can query jobs. Use the userType attribute

    try:
        response = table.query(

            KeyConditionExpression='#pk = :pk',
            ExpressionAttributeNames={
                '#pk': 'PK'
            },
            ExpressionAttributeValues={
                ':pk': f'USER#{username}'
            },
            ScanIndexForward=False

        )

        user = User(response['Items'][0])

        jobs = [Job(item).job_dict() for item in response['Items'][1:]]

        return user.user_jobs(jobs)



    except ClientError as err:
        logger.debug(f"Error occured when getting applications per job{err.response['Error']}")
        raise err
