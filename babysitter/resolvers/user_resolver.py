

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from resolvers.users.create_user_account import create_user_account as createUserAccount
from resolvers.users.get_user_account import get_user_account as getUserAccount
from resolvers.users.update_user_account import update_user_account as updateUserAccount
from resolvers.users.update_user_status import update_user_status as updateUserStatus

logger = Logger(child=True)
router = Router()


@router.resolver(type_name="Mutation", field_name="createUser")
def create_user(user=None):
    if user is None:
        user = {}
    return createUserAccount(user)


@router.resolver(type_name="Mutation", field_name="updateUser")
def update_user(user=None):
    if user is None:
        user = {}
    return updateUserAccount(user)


@router.resolver(type_name="Mutation", field_name="updateUserStatus")
def update_user_status(username: str = "", status: str = ""):
    return updateUserStatus(username, status)


@router.resolver(type_name="Query", field_name="getUser")
def get_user(username: str = ""):
    return getUserAccount(username)
