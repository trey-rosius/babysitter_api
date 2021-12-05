from typing import List, Dict, Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler.appsync import Router
from resolvers.applications.list_applications_per_job import listApplicationsPerJob
from resolvers.applications.apply import applyToJob

logger = Logger(child=True)
router = Router()


@router.resolver(type_name="Mutation", field_name="applyToJob")
def apply_to_job(application=None):
    if application is None:
        application = {}
    return applyToJob(application)


@router.resolver(type_name="Query", field_name="listApplicationsPerJob")
def list_applications_per_job(jobId: str = "") -> List[Dict[str, Any]]:
    return listApplicationsPerJob(jobId)
