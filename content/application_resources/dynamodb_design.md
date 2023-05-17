#### DynamoDB Table
Our dynamodb table stores all data related to the application.
<br />
Here's an illustration of the relationship between entities.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/babysitter_entity.png)

- There's a one to many relationship between User and Job. So a User(Parent) is allowed to create multiple jobs.
- There's also a one to many relationship between a Job and Application.

#### Primary Key Design
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/primary_key_design.png)

The User entity is actually unique on 2 attributes( username + email address)
<br />

That's why we have 2 PK and SK for User entity in the above table.
<br>
