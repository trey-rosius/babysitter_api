from typing import List

from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from entities.job_entity import JobEntity
from entities.application_entity import ApplicationEntity

from boto3.dynamodb.conditions import Key

from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
logger = Logger(service="list_applications_per_job")
tracer = Tracer(service="list_applications_per_job")

table = dynamodb.Table(os.environ["TABLE_NAME"])

@tracer.capture_method
def list_applications_per_job(jobId: str = ""):
    logger.debug(f'jobId is:{jobId}')

    try:
        response = table.query(
            IndexName="jobApplications",
            KeyConditionExpression=Key('GSI1PK').eq(f'JOB#{jobId}'),

            ScanIndexForward=False

        )

        logger.info(f'response is {response["Items"]}')
        job = JobEntity(response['Items'][0])
        logger.debug("job object is {}".format(job))

        applications = [ApplicationEntity(item).application_dict() for item in response['Items'][1:]]

        logger.debug({"application object is":applications})

        return job.job_application_dict(applications)


    except ClientError as err:
        logger.debug(f"Error occured when getting applications per job{err.response['Error']}")
        raise err
