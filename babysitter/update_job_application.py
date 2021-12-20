import json
import os
import boto3
from typing import Any, List, Literal, Union
from aws_lambda_powertools.utilities.batch import (BatchProcessor,
                                                   EventType,
                                                   FailureResponse,
                                                   SuccessResponse,
                                                   batch_processor)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer(service="update_job_application")
logger = Logger(service="update_job_application")


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
processor = BatchProcessor(event_type=EventType.SQS)

@tracer.capture_method
def record_handler(record: SQSRecord):
    """
    Handle messages from SQS Queue containing job applications.
    Update each application status to CLOSED
    """
    payload:str = record.body

    logger.info(f"payload has {len(payload)} records")

    if payload:
        logger.debug(" application item is {}".format(payload))
        item = json.loads(payload)
        response = table.update_item(
            Key={
                'PK': f"JOB#{item['jobId']}#APPLICATION#{item['id']}",
                'SK': f"JOB#{item['jobId']}#APPLICATION#{item['id']}"
            },
            ConditionExpression="attribute_exists(PK)",
            UpdateExpression="set jobApplicationStatus= :jobApplicationStatus",

            ExpressionAttributeValues={
                ':jobApplicationStatus': 'DECLINED'
            },
            ReturnValues="ALL_NEW"
        )

        logger.debug({' update response': response['Attributes']})



@logger.inject_lambda_context
@tracer.capture_lambda_handler
@batch_processor(record_handler=record_handler, processor=processor)
def lambda_handler(event, context: LambdaContext):
    batch = event["Records"]
    with processor(records=batch, processor=processor):
        processed_messages: List[Union[SuccessResponse, FailureResponse]] = processor.process()

    for messages in processed_messages:
        for message in messages:
            status: Union[Literal["success"], Literal["fail"]] = message[0]
            result: Any = message[1]
            record: SQSRecord = message[2]
            logger.debug("status is {}".format(status))
            logger.debug("result is {}".format(result))
            logger.debug("record is {}".format(record))
    return processor.response()