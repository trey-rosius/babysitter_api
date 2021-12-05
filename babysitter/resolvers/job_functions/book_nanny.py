from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from entities.Application import Application
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = Logger(service="book_nanny")
tracer = Tracer()

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
sqs = boto3.resource("sqs")
queue = sqs.Queue(os.environ["DELETE_FROM_CART_SQS_QUEUE"])


def bookNanny(username: str = "", jobId: str = "", applicationId: str = "", applicationStatus: str = ""):
    logger.info({f"Parameters {jobId, applicationId, applicationStatus}"})
    # first step involves get all applications for a the said job
    response = table.query(
        IndexName="jobApplications",
        KeyConditionExpression=Key('GSI1PK').eq(f'JOB#{jobId}'),

        ScanIndexForward=False

    )
    logger.info(f'response is {response["Items"]}')

    applications = [Application(item).application_dict() for item in response['Items'][1:]]

    logger.debug({"application object is": applications})
    try:

        response = client.transact_write_items(
            TransactItems=[{
                'Update': {
                    'TableName': os.environ["TABLE_NAME"],
                    "Key": {
                        "PK": {
                            "S": f'USER#{username}'
                        },
                        "SK": {
                            "S": f'JOB#{jobId}'
                        },
                    },
                    "ConditionExpression": "username = :username",
                    "UpdateExpression": "SET jobStatus = :jobStatus",
                    "ExpressionAttributeValues": {
                        ":username": {'S': username},
                        ":jobStatus": {'S': 'CLOSED'}
                    },
                    'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                }

            }, {
                'Update': {
                    'TableName': os.environ["TABLE_NAME"],
                    "Key": {
                        "PK": {
                            "S": f"JOB#{jobId}#APPLICATION#{applicationId}"
                        },
                        "SK": {
                            "S": f"JOB#{jobId}#APPLICATION#{applicationId}"
                        },
                    },
                    "UpdateExpression": "SET jobApplicationStatus= :jobApplicationStatus",
                    "ExpressionAttributeValues": {
                        ":jobApplicationStatus": {'S': applicationStatus},

                    },
                    'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                }
            }],
            ReturnConsumedCapacity='TOTAL',
            ReturnItemCollectionMetrics='SIZE'
        )
        logger.debug(f'transaction response is {response}')
        return True
    except ClientError as err:
        logger.debug(f"Error occurred during transact write{err.response}")
        logger.debug(f"Error occurred during transact write{err}")
        logger.debug(f"Error occurred during transact write{err.response['Error']}")
        if err.response['Error']['Code'] == 'TransactionCanceledException':
            if err.response['CancellationReasons'][0]['Code'] == 'ConditionalCheckFailed':
                errObj = Exception("You aren't authorized to make this update")

                raise errObj

        else:
            raise err
