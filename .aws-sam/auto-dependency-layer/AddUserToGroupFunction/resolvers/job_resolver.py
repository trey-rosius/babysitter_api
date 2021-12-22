from decimal import Decimal
from typing import Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from resolvers.jobs.create_job import create_job as createJob
from resolvers.jobs.book_nanny import book_nanny as bookNanny
from resolvers.jobs.list_all_jobs import list_all_jobs as listAllJobs
from resolvers.jobs.list_all_jobs_per_parent import list_all_jobs_per_parent as listAllJobsPerParent
from resolvers.jobs.jobs_applied_to import jobs_applied_to as jobsAppliedTo

logger = Logger(child=True)
router = Router()


@router.resolver(type_name="Mutation", field_name="createJob")
def create_job(job=None) -> Dict[str, Decimal]:
    if job is None:
        job = {}
    return createJob(job)


@router.resolver(type_name="Mutation", field_name="bookNanny")
def book_nanny(username: str = "", jobId: str = "", applicationId: str = "", jobApplicationStatus: str = ""):
    return bookNanny(username, jobId, applicationId, jobApplicationStatus)


@router.resolver(type_name="Query", field_name="listJobsPerParent")
def list_jobs_per_parent(username: str = "", type: str = ""):
    return listAllJobsPerParent(username, type)


@router.resolver(type_name="Query", field_name="listJobsAppliedTo")
def list_jobs_applied_to(username: str = ""):
    return jobsAppliedTo(username)


@router.resolver(type_name="Query", field_name="listAllJobs")
def list_all_jobs(jobStatus: str = ""):
    return listAllJobs(jobStatus)
