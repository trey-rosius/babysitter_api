#### DynamoDB Table
We'll be using a single table design structure to model the database.
Our dynamodb table stores all data related to the application.
<br />
If you don't know what single table design means, then this is a perfect moment to check out
the [DynamoDB Book](https://www.dynamodbbook.com/) by Alex Debrie.

After reading that book, you'll never go wrong with DynamoDB.

Let's proceed.

### User Entity Primary Key Design
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/primary_key_design.png)

The User entity is unique on 2 attributes( username + email address) and we'll see why, soon.
<br />
<br>
