from aws_lambda_powertools import Logger, Tracer
import boto3
import os

from botocore.exceptions import ClientError


dynamodb = boto3.resource("dynamodb")

logger = Logger(service="book_nanny")
tracer = Tracer()

client = boto3.client('dynamodb')


def bookNanny(username: str = "", jobId: str = "", applicationId: str = "", applicationStatus: str = ""):
    logger.info({f"Parameters {jobId, applicationId, applicationStatus}"})
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
