We'll start by installing and configuring [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/) and the boto3 library.
<br />
AWS Lambda Powertools is a suite of utilities for AWS Lambda functions to ease adopting best practices such as tracing, structured logging, custom metrics, and more.
<br />

Open up the `requirements.txt` file located at `babysitter_api/babysitter/` and paste these in it
<br />

```
aws-lambda-powertools==1.23.0
boto3
```
`aws-lambda-powertools` is a suite of utilities for AWS Lambda functions to ease adopting best practices such as tracing, structured logging, custom metrics, and more.
<br />

`boto3` is th AWS SDK for python, which can be use to create,configure and manage AWS services.
<br />

Open up your terminal from that directory and run the below command to install the libraries.
<br />

`pip install -r requirements.txt`
<br />

Next,open up `templates.yaml` file and enable Tracer and Logger utilities.
<br />
Tracer is an opinionated thin wrapper for AWS X-Ray Python SDK.
<br />
Logger provides an opinionated logger with output structured as JSON

**BEFORE**

```
Globals:
  Function:
    Timeout: 3
```
**AFTER**

```
Globals:
  Function:
    Tracing: Active
    Timeout: 3
    Environment:
      Variables:
        TABLE_NAME: !Ref DynamoDBBabySitterTable
        LOG_LEVEL: DEBUG
        POWERTOOLS_LOGGER_SAMPLE_RATE: 0.1
        POWERTOOLS_LOGGER_LOG_EVENT: true
        POWERTOOLS_SERVICE_NAME: "babysitter_api_service"
        POWERTOOLS_METRICS_NAMESPACE: "babysitter_api"

```