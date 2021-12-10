### What is the BabySitter App all about

## The Problem

So COVID came along and made Remote work possible. Yay!!!. Now we can work in our pyjamas, our bedrooms,sipping coffee from that large Mug we've always dreamt of. 
I don't know about you, but to me, working like this is a dream come true.
<br />
<br />
But as the saying goes, 
> When you pray for the rain, you've got to deal with the mud too

Working from home ain't all sunshine and merry making.
Most of us are parents, and for some sweet reason, our kids always decide to show how much they love us, during zoom meetings or when we want to put some work in.
<br />
<br />
They're either banging on the closed door or creating some noise with stuff from outside, because there's nobody to sit and put them to order.
<br />
<br />
There has to be a solution to this 🤔. Yeahhhh... Get a nanny.But then,other issues come in.
<br />

- Firstly, where or how do i get this nanny ?

- Supposing you meet them ,are you comfortable leaving your kids with somebody you just met ?

- How do you evaluate them to know if they are a good fit for your kids ?

- How can you speak to other parents that have worked with them in the past ?
  <br />
  And a ton of other questions.

BUT!!!!! 
<br />
What if there's an online website just for stuff like this. 
- Where you can meet people willing to carryout nanny duties.
- You can post job offers 
- See Nanny ratings based on previous jobs they've completed
- Book a nanny
- etc
<br />
That's the main purpose of this Project.
<br />
I don't intend to build the whole thing, but only to serve as a source of inspiration for some super ninja
out there who's willing to go all in on building something similar
<br />

## Proposed Solution

This REPO would contain all the code for the babysitter serverless GraphQL API.

## ENTITIES
- [x] User
- [x] Job
- [x] Application
- [ ] Ratings 

#### User

- Starting off with a simple structure, i'll assume there are only 3 types of users

- Admin
- Parent(Single or Couple)
- Nanny

#### Job

- Parents can put up a job posting like(We need somebody, aged between 21 and 40 to look after our son everyday from 8AM to 6PM.
- Job Type
- Schedule(Time and Date)
- Location
- Number of Kids
- Cost
- etc 

#### Applications
 - Somebody offering Nanny duties should be able to apply 
 to a job posted by a Parent.
 
#### Rate/Feedback 
 - Rate/Leave feedback on a nanny after job completion by a parent.
 - Rate/Leave Feedback on a parent after a job completion by a nanny.
 

#### User Profiles

##### Nanny attributes

- Full Names
- Date of Birth
- Gender
- Spoken languages
- Current Location
- Nationality
- Region of Origin
- National ID Card or Some Kind of identification
- Phone Number(Just of verification)
- Profile Picture
- Hourly Rate
- Level of Education
- Smoke/drink etc
- Any Disability
- Brief Description
- List of activities they can do

##### Parent attributes

- Full Names
- Location
- Date of Birth
- Phone Number(Just for Verification)
- List of Job postings

##### Admin

#### Ratings and Reviews

##### Nannys

- Answer a set of questions based on their experience with a Parent.
- Leave a brief review
- Leave a rating

##### Parents

- Answer a set of questions based on their experience with a Nanny.
- Leave a brief review
- Leave a rating

Reviews/Ratings will be publicly visible on each users profile.

#### Chats
- [ ] Not implemented



## Overview
This api is built as a serverless graphql api, using [Serverless Application
Module(SAM)](https://aws.amazon.com/serverless/sam/) for Infrastructure as Code, [AWS AppSync](https://aws.amazon.com/appsync/) for the serverless GraphQL, [AWS Cognito](https://aws.amazon.com/cognito/) for authentication,python 3.8 as the runtime language, [AWS Lambda](https://aws.amazon.com/lambda/) for direct lambda resolvers,
[Simple Queue Service(SQS)](https://aws.amazon.com/sqs/) for executing requests asynchronously, [AWS DynamoDB](https://aws.amazon.com/dynamodb/) for storing data.



### Access Patterns
- Create/Read/Update/Delete User account(Parent,Nanny)
- Update User Account Status(VERIFIED,UNVERIFIED,DEACTIVATED) by admin only
- Create Job(By Parent Only)
- Apply to Job(By Nanny Only)
- Book Nanny(By Parent Only)
- View all Open/Closed Jobs(By Nanny  or Admins Only)
- View all jobs applied to (By Nanny or admins only)
- View all applications for a job(By Parent or Admin only)
- View All jobs per parent(Only Parents or admin). A Parent can only view their jobs
- View All Nannies/Parents
- 

#### Solutions Architecture

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/babysitter_arch_api.png)

### INTRODUCTION
We'll be using [AWS AppSync](https://aws.amazon.com/appsync/) to build out our api. AWS AppSync is a fully managed service allowing developers to deploy scalable GraphQL backends on AWS.
<br />
It's flexibility lets you utilize new or existing tables, using either a single-table design or a multi-table approach.
<br />
This api uses the single table design approach.In a single table design, all our entities would be stored
in the same DynamoDB table. This let's us perform multiple queries on different entities in 
the same requests,that leads to a high efficiency as your app grows bigger.
<br />
<br />
This design approach has it's pros and cons, with one major con being the steep learning curve of modelling the 
single table. It requires you to know and understand your access patterns properly beforehand.
<br />
<br />
Here are the concepts we'll be covering in this article.
<br />
- We'll use Appsync to improve security and incorporate different access patterns
- We'll Implement Single Table Design. 
- We'll be using [aws lambda powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/) for tracing, structured logging, custom metrics and routing to properly 
route all Graphql endpoints.
- Build faster with the new SAM Cli (`sam sync --stack-name`)

We already highlighted our use case above. Now, let's dive into our DynamoDB table.
#### DynamoDB Table
Our dynamodb table stores all data related to the application.
<br />
<br />
Since we already understand our access patterns, let's dive right into the 
relationship between entities.

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/babysitter_entity.png)

- There's a one to many relationship between User and Job. So a User(Parent) is allowed to create multiple job.
- There's also a one to many relationship between a Job and Application

#### Primary Key Design
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/primary_key_design.png)

The User entity is actually unique on 2 attributes( username + email address)
<br />

That's why we have 2 PK and SK for User entity in the above table. 
<br>

From this current design, here are the access patterns available
1) Create/Read/Update/Delete User (Transaction Process) 
- `PK=USER#<Username>`
- `SK=USER#<Username>` 
- `PK=USEREMAIL#<Email>`
- `SK=USEREMAIL#<Email>`
2) Create/Update/Read/Delete Jobs 
- `PK=USER#<Username>` 
- `SK=JOB#<JobId>`
3) Create/Update Application 
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>` 
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
4) List all jobs per User
- `PK=USER#<Username>` 
- `SK= BEGINS_WITH('JOB#')` 
5) Book a Nanny (Transaction Process) 
- `PK=USER#<Username>` 
- `SK=JOB#<JobId>`
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>` 
- `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`
<br>

Booking a nanny means, changing the status of an application from `PENDING`  to `ACCEPTED` , while changing the 
job status from `OPEN` to `CLOSED`
<br>
<br>
The current design has limitations, There are a couple of access patterns it doesn't support yet.
For example, currently, we can't get all applications for a particular job.We need a Global Secondary index(GSI) for that. 
<br>
For this application, we'll create 3 GSI's for additional access patterns.
#### Global Secondary Indexes
1) `jobApplications`: Get applications for a job. Parents have to see all applications for the job
they posted, in-order to book who they intend to work with.
- `PK = GS1PK AND SK=GSI1SK`
2) `jobsAppliedTo`: A Nanny would definitely love to see all the jobs they applied to
- `PK = GSI2PK AND SK=GSI2SK`
3) `jobsByStatus`: It's essential to display OPEN jobs to job seekers. The system admin would also love
to see open /closed jobs.
- `PK = jobStatus AND SK=GSI1SK`

These are the few access patterns we'll cover in this tutorial.There's still a lot to add. You can take up the challenge and push forward.

#### GraphQL Schema
I won't paste the complete GraphQl schema here, just the relevant parts that need attention.
<br>
#### Mutations
```
        type Mutation {
            createUser(user:CreateUserInput!):User!
            @aws_cognito_user_pools

            updateUserStatus(username:String!,status:UserAccountStatus!):User
            @aws_cognito_user_pools(cognito_groups: ["admin"])

            updateUser(user:UpdateUserInput!):User!
            @aws_cognito_user_pools

            deleteUser(username:String!):Boolean
            @aws_cognito_user_pools


            createJob(job:CreateJobInput!):Job!
            @aws_cognito_user_pools(cognito_groups: ["parent"])

            applyToJob(application:CreateJobApplicationInput!):JobApplication!
            @aws_cognito_user_pools(cognito_groups: ["nanny"])

            bookNanny(username:String!,jobId:String!,applicationId:String!, jobApplicationStatus:JobApplicationStatus!):Boolean
            @aws_cognito_user_pools(cognito_groups: ["parent"])
        }

```
A user has to be authenticated before carrying out any `Mutation`.
<br />
Users are seperated into 3 user groups
- Admin
- Parent
- Nanny
Some Mutations can only be executed by Users of a particular group, while other
Mutations can be executed by Users of any group. 
<br />
<br />
For example, in the Mutation below, only an admin can change a User's account
status. Maybe from `UNVERIFIED` TO `VERIFIED` or vice versa
<br />
Here's the account status enum
```
        enum UserAccountStatus {
            VERIFIED
            UNVERIFIED
            DEACTIVATED
        }
```
.
```
updateUserStatus(username:String!,status:UserAccountStatus!):User
@aws_cognito_user_pools(cognito_groups: ["admin"])
```
Creating a job is reserved for Parent's only

```
  createJob(job:CreateJobInput!):Job!
  @aws_cognito_user_pools(cognito_groups: ["parent"])

```

Only Nanny's can apply to a job

```
 applyToJob(application:CreateJobApplicationInput!):JobApplication!
 @aws_cognito_user_pools(cognito_groups: ["nanny"])
```

Any User group can create an account
```
 createUser(user:CreateUserInput!):User!
 @aws_cognito_user_pools
```

#### Queries
Same User Group concept apply to queries.
```
        type Query {
            getUser(username: String!): User!  @aws_api_key @aws_cognito_user_pools

            listUser:[User]! @aws_cognito_user_pools(cognito_groups: ["admin","parent"])

            listAllJobs(jobStatus:String!):[Job]! @aws_cognito_user_pools(cognito_groups:["admin","nanny"])

            listJobsPerParent:User! @aws_cognito_user_pools(cognito_groups:["admin","parent"])

            listApplicationsPerJob(jobId:String!):Job!
            @aws_cognito_user_pools(cognito_groups:["admin","parent"])

            listJobsAppliedTo(username:String!):User!
            @aws_cognito_user_pools(cognito_groups:["admin","parent"])

        }
```
Here's the [complete schema](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/schema/schema.graphql)

## AWS IAM (Identity and Access Management) Policies
When i started learning how to build serverless applications. I almost went nuts wrapping my head 
head around AWS IAM.
<br />
A ton of serverless tutorials out there rarely talk about IAM and just dive into creating API's.
<br />
I think we should make a difference. 
<br />
#### What are IAM Policies
AWS services are born with zero permissions. You manage access in AWS by creating policies and attaching them to IAM identities (users, groups of users, or roles) or AWS resources. 
<br />
<br />
A policy is an object in AWS that, when associated with an identity or resource, defines their permissions.
AWS evaluates these policies when an IAM principal (user or role) makes a request.
<br />
In simple terms,
> policies define authorizations to AWS services and resources.

<br />
There are different types of Policies.

Let's take a look at an **identity-based policy(IAM Policy)** from the api we are about to build. 

```
  DynamoDBReadPolicy:
    Type: "AWS::IAM::Policy"
    Properties:
      PolicyName: DynamoDBReadPolicy
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          -
            Effect: "Allow"
            Action: [
              "dynamodb:GetItem",
              "dynamodb:Scan",
              "dynamodb:Query",
              "dynamodb:BatchGetItem",
              "dynamodb:DescribeTable"
              ]
            Resource:
              - !GetAtt DynamoDBHelloWorldTable.Arn
              - !Join [ '/',[!GetAtt DynamoDBHelloWorldTable.Arn,"index/*"]]
      Roles:
        - !Ref AddUserJobRole


```
This policy grants specific permissions to an AWS identity, thus giving them access to perform operations on 
 an Amazon DynamoDB. Policies have a specific format.
<br />

Here's what you should take note of, in the above policy
- Type `AWS::IAM::Policy`
- PolicyName `DynamoDBReadPolicy`
- Statement Effect `Allow` explicitly allows the role access to the resource.
- Action represent  a set of functions a role can have on the resource.
- Resource represents the aws resource the above actions would be performed on. 
In this case, it's our DynamoDB table and all it's respective Global Secondary Indexes.
- Roles: Attaching the above policy to a role(AWS Identity), grants them access to perform operations on 
 said Resource(DynamoDB)
<br />
`!Ref` is a cloud formation intrinsic function that returns the value of the specified resource.
<br />

We create an `AssumeRolePolicyDocument` and attach it to our lambda function that'll define all the permissions
it requires for it's execution.
Remember that, it's the same role we've attached the DynamoDB policy to.
<br />

Therefore once this role is attached to a lambda function, that function would have permissions to write to the 
dynamoDB table.

```
  AddUserJobRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Action:
            - "sts:AssumeRole"
            Effect: "Allow"
            Principal:
              Service:
                - "lambda.amazonaws.com"

```
Let's begin creating our api.
<br />
From your terminal, create a new SAM application by running the command `sam init` and following the prompts.
<br />
Take a look at the screenshots below 
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/s1.png)
![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/s2.png)





