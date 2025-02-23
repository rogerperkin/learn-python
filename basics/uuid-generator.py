import logging
from uuid import uuid4

# Setting up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Simulating CommonMessages class for the sake of this demo
class CommonMessages:
    JOB_ID = "Job ID:"

# Generate a unique job ID using uuid4()
job_id = uuid4()

# Log the job ID
logger.info(f"{CommonMessages.JOB_ID} {job_id}")
