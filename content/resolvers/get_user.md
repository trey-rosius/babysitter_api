#### Get User Endpoint.
- PK= `USER#<Username>`
- SK= `USER#<Username>`

1) Create a file called `get_user.py` inside `resolver/users` and type in the following code.
```
from aws_lambda_powertools import Logger, Tracer
import boto3
import os

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
        logger.debug("users dict {}".format(response))
        if response['Item'] is None:
            logger.debug("response is null")
            return {}
        else:
            logger.debug("response is not null")
            user = User(response['Item'])

            return user.user_dict()

```
We use DynamoDb's `get_item` function to get a particular user with identical PK and SK.
2) Add the endpoint to `user.py` file located at `resolvers/user_resolver.py`

```
@router.resolver(type_name="Query", field_name="getUser")
def get_user(username: str = ""):
    return getUser(username)

```
3) Add Resolver to Resources in `template.yml`
```
  GetUserResolver:
    Type: "AWS::AppSync::Resolver"
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId
      TypeName: "Query"
      FieldName: "getUser"
      DataSourceName: !GetAtt BabySitterFunctionDataSource.Name

```
Go ahead and deploy your app.
<br />
If you had `sam sync --stack-name babysitter --watch` running, once you hit save, the application synchronizes with the cloud.
Go ahead and test to make sure it works well.

#### Update User Status
While building this api, i assumed the system admin would at some point need a level of control over normal users(PARENT and NANNY) of the system.
<br />
So admins have the possibility to change a users account status to `VERIFIED`, `UNVERIFIED` OR `DEACTIVATED`.
<br />

If you plan on expanding this application, you can restrict a users access to the system,
based on the status of their account.That might be a good challenge for you.
<br />

As another challenge, try implementing this endpoint. I mean no to disrespect a boss like you.
I know you'll crush it with your left hand. 😤
<br />

Remember the solution is in the repo.
