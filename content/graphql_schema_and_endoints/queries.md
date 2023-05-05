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
