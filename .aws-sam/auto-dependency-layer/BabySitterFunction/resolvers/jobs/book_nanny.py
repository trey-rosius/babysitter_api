from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
import boto3
import os
import json

logger = Logger(service="book_nanny")
tracer = Tracer(service="book_nanny")
# client library
client = boto3.client("dynamodb")
# resource library
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN")
step_function_client = boto3.client("stepfunctions")


def book_nanny(
    username: str = "",
    jobId: str = "",
    applicationId: str = "",
    applicationStatus: str = "",
):
    logger.info({f"Parameters {jobId, applicationId, applicationStatus}"})
    # first step involves getting all applications for the said job
    input_json = {
        "input": {
            "username": username,
            "jobId": jobId,
            "applicationId": applicationId,
            "applicationStatus": applicationStatus,
        }
    }
    input_string = json.dumps(input_json)

    logger.debug("input string is".format(input_string))

    step_function_client.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=scalar_types_utils.make_id(),
        input=input_string,
    )
    return True
