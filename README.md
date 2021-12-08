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



##Overview
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

![alt text](https://raw.githubusercontent.com/trey-rosius/babysitter_api/master/babysitter_arch_2.png)

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
This design approach has it's pros and cons, with one major con of being the steep learning curve of modelling the 
single table. It requires you to know and understand your access patterns properly.
<br />
<br />
Here are the concepts we'll be covering in this article.
<br />
- We'll use Appsync to improve security and incorporate different access patterns
- We'll Implement Single Table Design. 
- We'll be using [aws lambda powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/) routing feature to properly 
route all Graphql endpoints.
- Build faster with the new SAM Cli (`sam sync --stack-name`)

We already highlighted our use case above. Now, let's dive into our dynamodb table.
#### DynamoDb Table
Our dynamodb table stores all data related to the application.It stores data on Users,
Jobs, applications, ratings etc. Those are the different entities we need to model.
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
- Create/Read/Update/Delete User (Transaction Process) (`PK=USER#<Username>`, `SK=USER#<Username>`  and `PK=USEREMAIL#<Email>`, `SK=USEREMAIL#<Email>`)
- Create/Update/Read/Delete Jobs (`PK=USER#<Username>` and `SK=JOB#<JobId>`)
- Create/Update Application (`PK=JOB#<JobId>#APPLICATION#<ApplicationId>` and `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`)
- List all jobs per User( `PK=USER#<Username>` and `SK= BEGINS_WITH('JOB#')` )
- Book a Nanny (Transaction Process) (`PK=USER#<Username>` and `SK=JOB#<JobId>`) (`PK=JOB#<JobId>#APPLICATION#<ApplicationId>` and `PK=JOB#<JobId>#APPLICATION#<ApplicationId>`)
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

#### AWS IAM (Identity and Access Management)
AWS services are born with zero permissions. It's your role as a developer to assign permissions and policies
to the services you intend to use.
<br />
<br />
With IAM, you can specify who can access which services and resources, and under which conditions
<br />
<br />
With IAM policies, you manage permissions to your workforce and systems to ensure least-privilege permissions.
<br />
<br />
Here's a list of all policies and permissions we'll use in this application


