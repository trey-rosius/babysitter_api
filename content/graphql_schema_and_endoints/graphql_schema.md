#### GraphQL Schema
```graphql
schema {
            query:Query
            mutation: Mutation
        }

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

        type Mutation {
            createUser(user:CreateUserInput!):User!
            @aws_cognito_user_pools
            updateUserStatus(username:String!,status:UserAccountStatus!):User
            @aws_cognito_user_pools(cognito_groups: ["admin"])
            updateUser(user:UpdateUserInput!):User!
            @aws_cognito_user_pools
            deleteUser(username:String!):Boolean
            createJob(job:CreateJobInput!):Job!
            @aws_cognito_user_pools(cognito_groups: ["parent"])
            applyToJob(application:CreateJobApplicationInput!):JobApplication!
            @aws_cognito_user_pools(cognito_groups: ["nanny"])
            bookNanny(username:String!,jobId:String!,applicationId:String!, jobApplicationStatus:JobApplicationStatus!):Boolean
            @aws_cognito_user_pools(cognito_groups: ["parent"])
        }

        type User @aws_cognito_user_pools {
            id: ID!
            username: String!
            email: AWSEmail!
            type:UserType!
            firstName:String!
            lastName:String!
            profilePicUrl:String!
            day:Int!
            month:Int!
            year:Int!
            dateOfBirth:AWSDate!
            age:Int!
            male:Boolean!
            female:Boolean!
            address:String!
            about:String!
            longitude:Float!
            latitude:Float!
            status:UserAccountStatus!
            postedJobs:[Job]
            createdOn:AWSTimestamp



        }
       type Job @aws_cognito_user_pools{
            id:ID!
            jobType:JobType!
            username:String!
            startDate:AWSDate!
            endDate:AWSDate!
            startTime:AWSTime!
            endTime:AWSTime!
            longitude:Float!
            latitude:Float!
            address:String!
            city:String!
            cost:Int!
            jobStatus:JobStatus!
            applications:[JobApplication]

       }
       type JobApplication @aws_cognito_user_pools{
           id:ID!
           username:String!
           jobId:String!
           jobApplicationStatus:JobApplicationStatus!
           createdOn:AWSTimestamp!
       }

        input CreateJobApplicationInput{
           username:String!
           jobId:String!
           jobApplicationStatus:JobApplicationStatus!
           createdOn:AWSTimestamp
        }

        input CreateJobInput{
            jobType:JobType!
            startDate:AWSDate!
            endDate:AWSDate!
            startTime:AWSTime!
            endTime:AWSTime!
            longitude:Float!
            latitude:Float!
            jobStatus:JobStatus!
            address:String!
            city:String!
            cost:Int!
            username:String!

        }

        input CreateUserInput {
            username: String!
            email: AWSEmail!
            type:UserType!
            firstName:String!
            lastName:String!
            profilePicUrl:String!
            day:Int!
            month:Int!
            year:Int!
            dateOfBirth:AWSDate!
            age:Int!
            male:Boolean!
            female:Boolean!
            address:String!
            about:String!
            longitude:Float!
            latitude:Float!
            status:UserAccountStatus!

        }
        input UpdateUserInput {
            username: String!
            email: AWSEmail!
            firstName:String!
            lastName:String!
            address:String!
            profilePicUrl:String
            day:Int!
            month:Int!
            age:Int!
            year:Int!
            dateOfBirth:AWSDate!
            male:Boolean!
            female:Boolean!
            about:String!
           longitude:Float!
            latitude:Float!

        }

        enum UserAccountStatus {
            VERIFIED
            UNVERIFIED
            DEACTIVATED
        }
        enum UserType{
            NANNY
            PARENT
        }
        enum JobType{
            BABYSITTING
            CLEANING
            RUNNING_ERRANDS

        }
        enum JobStatus{
            OPEN
            CLOSED
        }
        enum JobApplicationStatus{
            PENDING
            DECLINED
            ACCEPTED

        }

```
<br>
