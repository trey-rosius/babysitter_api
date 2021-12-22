from aws_lambda_powertools import Logger, Tracer
import boto3
import os

from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError

tracer = Tracer(service="create_user_resolver")
logger = Logger(service="create_user_resolver")

client = boto3.client('dynamodb')


@tracer.capture_method
def create_user_account(user=None):
    if user is None:
        user = {}
    logger.info(f'items:{user}')
    item: dict = {
        "id": scalar_types_utils.make_id(),
        "username": user['username'],
        "type": user['type'],
        "email": user['email'],
        "firstName": user["firstName"],
        "day": user["day"],
        "month": user['month'],
        "year": user['year'],
        "age": user['age'],
        "dateOfBirth": user['dateOfBirth'],
        "male": user['male'],
        "female": user['female'],
        "profilePicUrl": user['profilePicUrl'],
        "lastName": user["lastName"],
        "address": user["address"],
        "about": user["about"],
        "longitude": user["longitude"],
        "latitude": user["latitude"],
        "status": user["status"],

    }
    logger.debug(f'items:{item}')

    try:
        response = client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'Item': {
                            'PK': {
                                'S': f'USER#{item["username"]}'
                            },
                            'SK': {
                                'S': f'USER#{item["username"]}'
                            },
                            'GSI2PK': {
                                'S': f'USER#{item["username"]}'

                            },
                            'GSI2SK': {
                                'S': f'USER#{item["username"]}'

                            },
                            'id': {
                                'S': item["id"]
                            },
                            'username': {
                                'S': item["username"]
                            },
                            'type': {
                                'S': item["type"]
                            },
                            'email': {
                                'S': item['email']
                            },
                            'firstName': {
                                'S': item['firstName']
                            },
                            'lastName': {
                                'S': item['lastName']
                            },
                            'day': {
                                'N': item['day']
                            },
                            'month': {
                                'N': item['month']
                            },
                            'year': {
                                'N': item['year']
                            },
                            'male': {
                                'BOOL': item['male']
                            },
                            'female': {
                                'BOOL': item['female']
                            },
                            'dateOfBirth': {
                                'S': item['dateOfBirth']
                            },
                            'profilePicUrl': {
                                'S': item['profilePicUrl']
                            },
                            'address': {
                                'S': item['address']
                            },
                            'about': {
                                'S': item['about']
                            },
                            'longitude': {
                                'N': f"{item['longitude']}"
                            },
                            'latitude': {
                                'N': f"{item['latitude']}"
                            },
                            'status': {
                                'S': item['status']
                            },
                            'createdOn': {
                                'N': f'{scalar_types_utils.aws_timestamp()}'
                            }

                        },
                        'TableName': os.environ["TABLE_NAME"],
                        'ConditionExpression': "attribute_not_exists(PK)"

                    },

                },
                {
                    'Put': {
                        'Item': {
                            'PK': {
                                'S': f'USEREMAIL#{item["email"]}'
                            },
                            'SK': {
                                'S': f'USEREMAIL#{item["email"]}'
                            },

                            'id': {
                                'S': item["id"]
                            },
                            'username': {
                                'S': item["username"]
                            },

                            'email': {
                                'S': item['email']
                            },

                        },
                        'TableName': os.environ["TABLE_NAME"],
                        'ConditionExpression': "attribute_not_exists(PK)"

                    }
                }
            ]
        )
        tracer.put_annotation("CREATE_USER_TRANSACTION", "SUCCESS")
        logger.debug(f'transaction response is {response}')
        return item
    except ClientError as err:
        logger.debug(f"Error occurred during transact write{err.response}")
        logger.debug(f"Error occurred during transact write{err}")
        logger.debug(f"Error occurred during transact write{err.response['Error']}")
        if err.response['Error']['Code'] == 'TransactionCanceledException':
            if err.response['CancellationReasons'][0]['Code'] == 'ConditionalCheckFailed':
                # TODO make exception handling DRY
                errObj = Exception("Username already exist")

                raise errObj
            elif err.response['CancellationReasons'][1]['Code'] == 'ConditionalCheckFailed':
                # TODO make exception handling DRY
                errObj = Exception("Email already exist")

                raise errObj

        else:
            raise err
