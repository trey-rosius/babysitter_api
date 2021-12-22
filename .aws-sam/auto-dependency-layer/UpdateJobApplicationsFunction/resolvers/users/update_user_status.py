from aws_lambda_powertools import Logger, Tracer
import boto3
import os


from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
tracer = Tracer(service="update_user_status")
logger = Logger(service="update_user_status")

table = dynamodb.Table(os.environ["TABLE_NAME"])

@tracer.capture_method
def update_user_status(username: str = "", status: str = ""):
    logger.debug(f'update user status :{username} , {status}')

    try:
        response = table.update_item(
            Key={
                'PK': f'USER#{username}',
                'SK': f'USER#{username}'
            },
            ConditionExpression="attribute_exists(PK)",
            UpdateExpression="set #status= :status",
            ExpressionAttributeNames={
                '#status':'status'
            },
            ExpressionAttributeValues={
                ':status': status
            },
            ReturnValues="ALL_NEW"
        )

        logger.debug({' update response':response['Attributes']})
        return response['Attributes']

    except ClientError as err:
        logger.debug(f"Error occurred during user update status{err.response['Error']}")
        raise err
