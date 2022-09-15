from rq import Queue

from .. import redis_jobs

# The background_job method will be implemented in the service that runs
# the rq worker process.
BACKGROUND_JOB_METHOD = "app.main.jobs.background_job"

JOB_QUEUE_HIGH = "high"
JOB_QUEUE_DEFAULT = "default"
JOB_QUEUE_LOW = "low"


def queue_job(*, name, params, queue):
    q = Queue(name=queue, connection=redis_jobs.connection)
    q.enqueue(BACKGROUND_JOB_METHOD, {"name": name, "params": params})
