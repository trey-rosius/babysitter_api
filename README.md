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
