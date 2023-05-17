#### Create user
The first resolver we'll create for our api is  `create_user`. It is the gateway into our app.
We want users to be able to create an account.
For a user account to be unique, we apply a unique constraint on 2 attributes
- username
- email
No 2 users can have same username and email. We'll use a conditional expression to ensure uniqueness,then use 2 put request inside a dynamodb transaction api.
<br />

DynamoDb transactions provide developers with atomicity, consistency, isolation, and durability (ACID) across tables. It processes requests in batches. If one request in the batch
fails, the whole batch fails. The batch succeeds, when all requests succeed and that's exactly the use case we want.
<br />

Inside the `resolvers` function, create a folder called `users` and inside of users folder, create a file called `create_user_account.py` and type in the following code.

```
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
                                'N': f"{item['day']}"
                            },
                            'month': {
                                'N': f"{item['month']}"
                            },

                            'year': {
                                'N': f"{item['year']}"
                            },
                            'age': {
                                'N': f"{item['age']}"

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

```
Firstly, we initiate tracer, logger and the boto3 client library.Then we annotate the function
with `@tracer.capture_method` to capture function metadata.
<br />

Next, we have the method `transact_write_items` which takes 2 put requests, one for username and the other for email.
This transaction is wrapped in a try except clause, so that we can catch relevant errors and send back to the client app.
<br />

Errors like
- username already exist
- email already exist

Next, create a file called `user.py` inside of `resolvers` folder and type in the following code

```
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from resolvers.users.create import createUser

logger = Logger(child=True)
router = Router()


@router.resolver(type_name="Mutation", field_name="createUser")
def create_user(user=None):
    if user is None:
        user = {}
    return createUser(user)

```
In the above code, we initialize the router and logger classes. Because our app has multiple resolvers, we use the router feature to
separate files and ease maintenance.
<br />

We use `@router.resolver()` decorator to make our functions match graphQL types and fields.
<br />

We now have to import this class(`create.py`) in `app.py` lambda function.
<br />
In `app.py` file, type in the following code

```
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler import AppSyncResolver

from resolvers import  user

tracer = Tracer(service="lambda_function")
logger = Logger(service="lambda_function")

app = AppSyncResolver()
app.include_router(user.router)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.debug(f'event is {event}')
    return app.resolve(event, context)


```
Take note of the way we initialize `AppSyncResolver` and include the `user.router` we defined in the previous class.

Before running our app, we have to add a resolver resource, under `Resource` in `template.yaml`.

```
  CreateUserResolver:
    Type: "AWS::AppSync::Resolver"
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId
      TypeName: "Mutation"
      FieldName: "createUser"
      DataSourceName: !GetAtt BabySitterFunctionDataSource.Name

```
Take note of the `TypeName` and `FieldName` which corresponds to what we have in the GraphQl Schema.
Also, the `DataSourceName` that points to our Lambda Datasource.
<br />

In-order to run this app the SAM Accelerate way, we use the command
`sam sync --stack-name babysitter_api`
The `sam sync` command with no options deploys or updates all infrastructure and code like the `sam deploy` command.
<br />
However, unlike `sam deploy`, `sam sync` bypasses the AWS CloudFormation changeset process.
<br />
First, `sam sync` builds the code using the `sam build` command and then the application is synchronized to the cloud.
<br />
Once your application successfully deploys, log into the aws console, search and open up cognito from the search bar.
<br />
 ![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/a.png)
<br />

Click on Manage User Pools and then click on your app's user pool. Mine's `babysitter-UserPool`.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/b.png)

<br />
Click on Users and groups on the left, then create user.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/c.png)

<br />
Fill in the fields, like i've done in the screenshot below and click create user.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/d.png)

Search and open up appsync from the search bar.
<br />
Click and open up your api.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/g.png)

Click on `queries` on the left hand side menu, make sure API key is selected as the authorization provider,
fill in the `createUser` mutation and run it.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/h.png)

Because we restricted our endpoint to authenticated users only(by adding the ` @aws_cognito_user_pools` decorator to the endpoint), you'll get an `Unauthorized` errorType when
you access the endpoint as an unauthenticated user.

Click on API key and select your cognito user pools ID.
<br />
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/i.png)

Sign in using the user credentials you created in the cognito screen above.
<br />

Now Run the Mutation again.
<br />
If everything goes successfully, you should see output similar to this.
<br />

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/e.png)

If you run the Mutation again, you should see this output

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/f.png)
<br />
<br />
Here's a frontend workflow of the complete process from user sign up to account creation.
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/babysitter_signup_workflow.png)

<br />
If you run into any issues, don't forget to open up cloudwatch and checkout the lambda logs. Remember we
are using logger and tracer to debug our endpoints. Be sure to make good use of them.
