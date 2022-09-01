from pytest_bdd import scenarios, when, parsers, then
import pytest

from lib.api.job_status_api import JobStatus
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/job_status-post.feature')


@when(parsers.cfparse('job_status request with {task:String} is send', extra_types=EXTRA_STRING_TYPES))
def job_status_response(task):
    parameters = Constructor.job_status_payload(task=task)
    pytest.response = JobStatus.post(parameters)
    print(pytest.response)


@then(parsers.cfparse('response body should be "{body:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(body):
    assert pytest.response.text == f'{body}'
