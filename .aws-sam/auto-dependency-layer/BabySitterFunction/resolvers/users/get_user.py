from aws_lambda_powertools import Logger, Tracer
import boto3
import os
import json

from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError
from entities.User import User

dynamodb = boto3.resource("dynamodb")
tracer = Tracer(service="get_user")
logger = Logger(service="get_user")

table = dynamodb.Table(os.environ["TABLE_NAME"])


@tracer.capture_method
def getUser(username: str = ""):
    logger.debug(f'username is:{username}')

    try:
        response = table.get_item(
            Key={
                'PK': f'USER#{username}',
                'SK': f'USER#{username}'
            }
        )
        user = User(response['Item'])
        logger.info("users dict {}".format(response['Item']))
        return user.user_dict()



    except ClientError as err:
        logger.debug(f"Error occured during get users item {err.response['Error']}")
        raise err
