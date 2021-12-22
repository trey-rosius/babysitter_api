from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from entities.job_entity import JobEntity
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
logger = Logger(service="list_all_jobs")
tracer = Tracer()

table = dynamodb.Table(os.environ["TABLE_NAME"])

@tracer.capture_method
def list_all_jobs(jobStatus: str = ""):
    logger.debug(f'jobStatus is:{jobStatus}')

    try:
        response = table.query(
            IndexName="getJobsByStatus",
            KeyConditionExpression=Key('jobStatus').eq(jobStatus),
            ScanIndexForward=False

        )

        logger.info(f'response is {response["Items"]}')
        jobs = [JobEntity(item).job_dict() for item in response['Items']]

        logger.debug({"jobs list is": jobs})
        return jobs


    except ClientError as err:
        logger.debug(f"Error occured when getting applications per jobs{err.response['Error']}")
        raise err
