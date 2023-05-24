#### Mutations
Mutations are used to modify content on the server-side.
Here are the mutations for the api.

```
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

```
A user has to be authenticated before carrying out any `Mutation`.
<br />

Users are separated into 3 groups
- Admin
- Parent
- Nanny

Some Mutations can only be executed by Users of a particular group, while other
Mutations can be executed by Users of any group.
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
