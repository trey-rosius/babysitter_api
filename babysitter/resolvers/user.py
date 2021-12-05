

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from resolvers.users.create import createUser
from resolvers.users.get_user import getUser
from resolvers.users.update_user_status import updateUserStatus

logger = Logger(child=True)
router = Router()


@router.resolver(type_name="Mutation", field_name="createUser")
def create_user(user=None):
    if user is None:
        user = {}
    return createUser(user)


@router.resolver(type_name="Mutation", field_name="updateUserStatus")
def update_user_status(username: str = "", status: str = ""):
    return updateUserStatus(username, status)


@router.resolver(type_name="Query", field_name="getUser")
def get_user(username: str = ""):
    return getUser(username)
