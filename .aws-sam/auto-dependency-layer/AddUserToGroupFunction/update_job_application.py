import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer(service="update_job_application")
logger = Logger(service="update_job_application")


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    Handle messages from SQS Queue containing applications.
    Update each application status CLOSED
    """

    records = event["Records"]
    logger.info(f"updating {len(records)} records")

    for item in records:
        logger.debug(" application item is {}".format(item['body']))
        item_body = json.loads(item["body"])
        response = table.update_item(
            Key={
                'PK': f"JOB#{item_body['jobId']}#APPLICATION#{item_body['id']}",
                'SK': f"JOB#{item_body['jobId']}#APPLICATION#{item_body['id']}"
            },
            ConditionExpression="attribute_exists(PK)",
            UpdateExpression="set jobApplicationStatus= :jobApplicationStatus",

            ExpressionAttributeValues={
                ':jobApplicationStatus': 'DECLINED'
            },
            ReturnValues="ALL_NEW"
        )

        logger.debug({' update response': response['Attributes']})
    return {
        "statusCode": 200,
    }
