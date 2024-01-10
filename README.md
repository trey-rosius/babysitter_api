## Serverless GraphQL API A Nanny APP

This project has been well documented and is currently being served on EduCloud Academy.

https://www.educloud.academy/

Follow that link to learn more about accelerating your cloud skills through hands on labs
### content structure


```
content
  |- Introduction
      |- the_problem.md
      |- proposed_solution.md
      |- overview.md
      |- introduction.md
  |- Application Resoure
      |- dynamo_db_design.md
      |- access_patters.md
      |- global_secondary_index.md
  |-  GraphQL Schema and Endpoints
      |- graphql_schema.md
      |- mutations.md
      |- queries.md
  |-  create_api
      |- initialize_sam_project.md
      |- installing_lambda_powertools.md
      |- cognito_user_pools_and_graphql_api.md
      |- roles_and_policies.md
      |- datasources.md
  |-  Resolvers
      |- create_user.md
      |- update_user.md
      |- get_user.md
      |- create_job.md
      |- list_all_jobs.md
      |- apply_to_job.md
      |- book_a_nanny.md
      |- designing_step_function_workflow.md
      |- add_sqs_queue.md
      |- add_state_machine_resource.md
 |-   Conclusion
      |- conclusion.md

```

Load testing results of the book_nanny endpoint, when using step functions versus using lambda.
Step functions did the task within half the time it took for lambda to get it done

## Express Step Functions Workflow

```
Requests      [total, rate,  throughput]
               3000,  50.02, 49.75
              ------------------------------------
Duration      [total, attack, wait]
              1m0s,   59.98s, 327.514ms
              --------------------------------------
Latencies     [min,      mean,      50,        90,        95,        99,       max]
              260.937ms, 373.937ms, 343.769ms, 480.176ms, 544.639ms, 928.78ms, 1.555s
              ----------------------------------------------------------------------
```

## Lambda Function

```
Requests      [total, rate,  throughput]
               3000,  50.02, 49.26
              --------------------------------------------------------------------
Duration      [total, attack,  wait]
               1m1s,  59.976s, 930.822ms
              -------------------------------------------------------------------
Latencies     [min,       mean,      50,        90,       95,        99,     max]
               267.713ms, 549.823ms, 457.517ms, 606.87ms, 720.902ms, 2.723s, 3.432s
              ---------------------------------------------------------------------

```

## Local Development & Testing

You can deploy the application on your local machine without needing an AWS account, using LocalStack. LocalStack is a cloud emulator that runs various AWS services on your local machine. It spins up a testing environment on your local machine that provides the same functionality and APIs as the real AWS cloud environment.

To run the application locally, you need to setup the following prerequisites on your machine:

- [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/)
- [Docker](https://docs.docker.com/get-docker/)
- [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) & [`samlocal` script](https://github.com/localstack/aws-sam-cli-local)

### Run LocalStack

Before you can run the application locally, you need to start LocalStack. You can do this by running the following command:

```bash
export LOCALSTACK_AUTH_KEY=<YOUR_AUTH_KEY>
localstack start -d
```

> If you don't have an auth key, you can get one by creating an account on [LocalStack Web Application](https://app.localstack.cloud/) and signing up for a [Hobby Plan](https://app.localstack.cloud/pricing).

### Build the application

You can build the SAM application by running the following command:

```bash
sam build --use-container  
```

### Deploy the application

After successfully building the application, you can deploy it locally by running the following command:

```bash
samlocal deploy --resolve-s3
```

The `samlocal` script is a wrapper around the `sam` CLI that configures the endpoint URL parameter for each AWS service to point to the LocalStack container.

After a successful deployment, you should see the following output:

```bash
CloudFormation outputs from deployed stack
------------------------------------------------------------------------------------------------------------------------------
Outputs                                                                                                                      
------------------------------------------------------------------------------------------------------------------------------
Key                 BabySitterFunction                                                                                       
Description         Baby Sitter Lambda Function ARN                                                                          
Value               arn:aws:lambda:us-east-2:000000000000:function:babysitter-api-BabySitterFunction-408fbb55                

Key                 UpdateJobApplicationsFunction                                                                            
Description         Baby Sitter Lambda Function ARN                                                                          
Value               arn:aws:lambda:us-east-2:000000000000:function:babysitter-api-UpdateJobApplicationsFun-5dc02b4b          

Key                 BabySitterAPI                                                                                            
Description         -                                                                                                        
Value               arn:aws:appsync:us-east-2:000000000000:apis/3e0b4c6ec0004ba782701b6b2e                                   
------------------------------------------------------------------------------------------------------------------------------

Successfully created/updated stack - babysitter-api in us-east-2
```
