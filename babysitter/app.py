from aws_lambda_powertools import Logger, Tracer
import boto3
import os

from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler import AppSyncResolver
from user.create import create
from user.get_user import get
from user.update_user_status import updateUserStatus

from job.create import createJob
from job_applications.apply import applyToJob
from job_applications.list_applications_per_job import listApplicationsPerJob
from job.list_all_jobs_per_parent import listAllJobsPerParent
from job.list_all_jobs import listAllJobs
from job.jobs_applied_to import jobsAppliedTo
from job.book_nanny import bookNanny

from aws_lambda_powertools.utilities.data_classes.appsync import scalar_types_utils
from botocore.exceptions import ClientError

tracer = Tracer(service="sample_resolver")
logger = Logger(service="sample_resolver")

client = boto3.client('dynamodb')
app = AppSyncResolver()


# Note that `creation_time` isn't available in the schema
# This utility also takes into account what info you make available at API level vs what's stored


@app.resolver(type_name="Mutation", field_name="createUser")
def create_user(user: dict = {}):
    return create(user)


@app.resolver(type_name="Mutation", field_name="updateUserStatus")
def update_user_status(username: str = "", status: str = ""):
    return updateUserStatus(username, status)


@app.resolver(type_name="Query", field_name="getUser")
def get_user(username: str = ""):
    return get(username)


@app.resolver(type_name="Mutation", field_name="createJob")
def create_job(job: dict = {}):
    return createJob(job)


@app.resolver(type_name="Mutation", field_name="applyToJob")
def apply_to_job(application: dict = {}):
    return applyToJob(application)


@app.resolver(type_name="Mutation", field_name="bookNanny")
def book_nanny(username: str = "", jobId: str = "", applicationId: str = "", jobApplicationStatus: str = ""):
    return bookNanny(username, jobId, applicationId, jobApplicationStatus)


@app.resolver(type_name="Query", field_name="listApplicationsPerJob")
def list_applications_per_job(jobId: str = ""):
    return listApplicationsPerJob(jobId)


@app.resolver(type_name="Query", field_name="listJobsPerParent")
def list_jobs_per_parent(username: str = "", type: str = ""):
    return listAllJobsPerParent(username, type)


@app.resolver(type_name="Query", field_name="listJobsAppliedTo")
def list_jobs_applied_to(username: str = ""):
    return jobsAppliedTo(username)


@app.resolver(type_name="Query", field_name="listAllJobs")
def list_all_jobs(jobStatus: str = ""):
    return listAllJobs(jobStatus)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.debug(f'event is {event}')
    logger.debug(f'context is {context}')
    return app.resolve(event, context)
