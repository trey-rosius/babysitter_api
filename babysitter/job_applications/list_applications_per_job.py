from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from entities.Job import Job
from entities.Application import Application
import json
from decima_encoder import DecimalEncoder
import decimal
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from boto3.dynamodb.conditions import Key

from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
logger = Logger(service="sample_resolver")

table = dynamodb.Table(os.environ["TABLE_NAME"])


def listApplicationsPerJob(jobId: str = ""):
    logger.debug(f'jobId is:{jobId}')

    try:
        response = table.query(
            IndexName="jobApplications",
            KeyConditionExpression=Key('GSI1PK').eq(f'JOB#{jobId}'),

            ScanIndexForward=False

        )

        logger.info(f'response is {response["Items"]}')
        job = Job(response['Items'][0])

        applications = [Application(item).application_dict() for item in response['Items'][1:]]

        logger.debug({"application object is":applications})
        return job.job_application_dict(applications)


    except ClientError as err:
        logger.debug(f"Error occured when getting applications per job{err.response['Error']}")
        raise err
