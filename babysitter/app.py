from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler import AppSyncResolver

from resolvers import job_resolver, user_resolver, application_resolver

tracer = Tracer(service="lambda_function")
logger = Logger(service="lambda_function")

app = AppSyncResolver()
app.include_router(job_resolver.router)
app.include_router(user_resolver.router)
app.include_router(application_resolver.router)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.debug(f'event is {event}')
    return app.resolve(event, context)
