from aws_lambda_powertools import Logger, Tracer
import boto3
import os
from decimal import Decimal

from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
tracer = Tracer(service="update_user")
logger = Logger(service="update_user")

table = dynamodb.Table(os.environ["TABLE_NAME"])


@tracer.capture_method
def update_user_account(user=None):
    if user is None:
        user = {}
    logger.info(f'items:{user}')

    item: dict = {

        "username": user['username'],
        "email": user['email'],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "address": user["address"],
        "profilePicUrl": user['profilePicUrl'],
        "day": user["day"],
        "month": user['month'],
        "year": user['year'],
        "age": user['age'],
        "dateOfBirth": user['dateOfBirth'],
        "male": user['male'],
        "female": user['female'],
        "about": user["about"],
        "longitude": Decimal(f"{user['longitude']}"),
        "latitude": Decimal(f"{user['latitude']}"),

    }
    logger.debug(f'items:{item}')

    try:
        response = table.update_item(
            Key={
                'PK': f'USER#{item["username"]}',
                'SK': f'USER#{item["username"]}'
            },
            ConditionExpression="attribute_exists(PK)",
            UpdateExpression="set firstName= :firstName,lastName= :lastName, "
                             "profilePicUrl=:profilePicUrl,"
                             "address= :address,about= :about,male =:male,female= :female,age= :age,dateOfBirth= "
                             ":dateOfBirth,#day=:day,#month= :month,#year= :year,"
                             "longitude= :longitude,latitude= :latitude",
            ExpressionAttributeNames={
                '#day': 'day',
                '#month': 'month',
                '#year': 'year',

            },

            ExpressionAttributeValues={

                ":firstName": item['firstName'],
                ":lastName": item['lastName'],
                ":address": item['address'],
                ":profilePicUrl": item['profilePicUrl'],
                ":male": item['male'],
                ":female": item['female'],
                ":age": item['age'],
                ":dateOfBirth": item['dateOfBirth'],
                ":day": item['day'],
                ":month": item['month'],
                ":year": item['year'],
                ":about": item['about'],
                ":longitude": item['longitude'],
                ":latitude": item['latitude'],

            },
            ReturnValues="ALL_NEW"
        )

        logger.debug({' update response': response['Attributes']})
        return response['Attributes']

    except ClientError as err:
        logger.debug(f"Error occurred during user update{err.response['Error']}")
        raise err
