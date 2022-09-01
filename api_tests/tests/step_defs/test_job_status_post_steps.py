from pytest_bdd import scenarios, when, parsers, then, given
import pytest

from lib.api.ds2ws_api import Ds2ws
from lib.api.job_status_api import JobStatus
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/job_status-post.feature')


@when(parsers.cfparse('job_status request with "{task:String}" is send', extra_types=EXTRA_STRING_TYPES))
def job_status_response(task):
    parameters = Constructor.job_status_payload(task=task)
    pytest.response = JobStatus.post(parameters)


@when(parsers.cfparse('job_status request is send'))
def job_status_response(task_id):
    parameters = Constructor.job_status_payload(task=task_id)
    pytest.response = JobStatus.post(parameters)


@given(parsers.cfparse('ws dataset is derived from it'),target_fixture='task_id')
def task_id(dataset, unique_ds_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ds_name)
    response = Ds2ws.post(parameters)
    return response.json()["task_id"]


@then(parsers.cfparse('response body should be "{body:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(body):
    assert pytest.response.text == f'{body}'
