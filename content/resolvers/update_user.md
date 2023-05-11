### Update User
- PK= `USER#<Username>`
- SK= `USER#<Username`
<br />

One of the access patterns of our application, is to give the user the possibility to update their accounts.
<br />
There's just a couple of attributes they are allowed to update though.
```
        "firstName",
        "lastName",
        "address",
        "about",
        "longitude",
        "latitude",

```
They aren't allowed to update their account status. That access point would be reserved for the admin only.
<br />

Other attributes they can't update are Username, email, UserType.
<br />

An account can only be updated, if the primary key already exists. So we'll use 
dynamoDB's `ConditionExpression="attribute_exists(PK)"` to ensure they account exists before updating.
<br />

Create a file called `update_user_account.py` inside `resolvers/users/` directory and type in the following code.
```
from aws_lambda_powertools import Logger, Tracer
import boto3
import os


from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
tracer = Tracer(service="update_user")
logger = Logger(service="update_user")

table = dynamodb.Table(os.environ["TABLE_NAME"])


@tracer.capture_method
def updateUser(user=None):
    if user is None:
        user = {}
    logger.info(f'items:{user}')

    item: dict = {

        "username": user['username'],
        "email": user['email'],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "address": user["address"],
        "about": user["about"],
        "longitude": user['longitude'],
        "latitude": user['latitude'],

    }
    logger.debug(f'items:{item}')

    try:
        response = table.update_item(
            Key={
                'PK': f'USER#{item["username"]}',
                'SK': f'USER#{item["username"]}'
            },
            ConditionExpression="attribute_exists(PK)",
            UpdateExpression="set firstName= :firstName,lastName= :lastName,address= :address,about= :about,"
                             "longitude= :longitude,latitude= :latitude",

            ExpressionAttributeValues={

                ":firstName": item['firstName'],
                ":lastName": item['lastName'],
                ":address": item['address'],
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

```

Take note of the `ConditionExpression`, the `UpdateExpression` and the `ExpressionAttributeValues`.

Add the `updateUser` endpoint to the `resolvers/user.py` file.

```
@router.resolver(type_name="Mutation", field_name="updateUser")
def update_user(user=None):
    if user is None:
        user = {}
    return updateUser(user)

```
Then add the Resolver under Resources in `template.yaml`.
```
  UpdateUserResolver:
    Type: "AWS::AppSync::Resolver"
    Properties:
      ApiId: !GetAtt BabySitterApi.ApiId
      TypeName: "Mutation"
      FieldName: "updateUser"
      DataSourceName: !GetAtt BabySitterFunctionDataSource.Name

```
Run the command `sam sync --stack-name babysitter` and build and synchronize the application.
<br />
Let's test the endpoint. Same as above, navigate to appsync console, open up the babysitter app, click on Queries and run the 
`updateUser` Mutation. 
<br />

You'll hit an error like this.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/p.png)

`Float Types are not supported.Use Decimal types instead`

<br />
This issue is related to the longitude and latitude values. They are float values and aren't supported
by DynamoDB yet. So we have to convert them to Decimal types.
<br />

Navigate to `update_user_account.py` file and add the Decimal import 
`from decimal import Decimal`

<br />
Next, convert this 

```
"longitude": user['longitude'],
 "latitude": user['latitude'],

```
Into this 

```
 "longitude": Decimal(f"{user['longitude']}"),
  "latitude": Decimal(f"{user['latitude']}"),

```
So your item dictionary now looks like this

```
   item: dict = {

        "username": user['username'],
        "email": user['email'],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "address": user["address"],
        "about": user["about"],
        "longitude": Decimal(f"{user['longitude']}"),
        "latitude": Decimal(f"{user['latitude']}"),

    }
```
Here's where you'll witness the true power of SAM ACCELERATE.
<br />

When you update a function this way, you don't have to deploy the complete application using 
`sam sync --stack-name babysitter` anymore.
<br />

Using the command `sam sync --stack-name babysitter --code`  instructs AWS SAM to sync all the code resources in the stack
in about 7 seconds.
<br />
Please go ahead the try it out.
<br />

>The SAM team went wild with this one.😁 

<br />
So you can build and test out new features of your app real quick. 
<br />

Another sweet command is Sam sync watch.
<br />

The `sam sync --watch` option tells AWS SAM to monitor for file changes and automatically synchronize when changes are detected.
<br />

If the changes include configuration changes, AWS SAM performs a standard synchronization equivalent to the `sam sync` command. 
<br />

If the changes are code only, then AWS SAM synchronizes the code with the equivalent of the `sam sync --code` command.
<br />

The first time you run the `sam sync` command with the `--watch flag`, AWS SAM ensures that the latest code and infrastructure are in the cloud. It then monitors for file changes until you quit the command:

`sam sync --stack-name babysitter --watch`
<br />

After syncing your app, go ahead and test out the `updateUser` mutation once more and confirm that it works as expect.

### Moving Forward
From this point on, we'll be looking at the code only and you'll be doing the testing in appsync and making sure everything works well.
<br />

Remember that the repo has code, which you can always jump back to, incase you missed something.
<br />
