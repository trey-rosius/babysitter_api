import json
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger, Tracer
import boto3

client = boto3.client("cognito-idp")

tracer = Tracer(service="add_user_to_a_group")
logger = Logger(service="add_user_to_group")


def lambda_handler(event, context):
    logger.debug("event {}".format(event))
    logger.debug("group name {}".format(event["request"]["clientMetadata"]["group"]))

    try:
        response = client.admin_add_user_to_group(
            GroupName=event["request"]["clientMetadata"]["group"],
            UserPoolId=event["userPoolId"],
            Username=event["userName"],
        )
        logger.debug("response {}".format(response))
        return response
    except ClientError as err:
        logger.debug("error{}".format(err))
        raise err
