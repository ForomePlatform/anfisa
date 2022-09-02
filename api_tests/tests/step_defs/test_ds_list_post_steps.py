import pytest
import time
from pytest_bdd import scenarios, when, parsers, then

from lib.api.ds_list_api import DsList
from lib.api.job_status_api import JobStatus
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ds_list-post.feature')


@when(parsers.cfparse('ds_list request is send'))
def ds_list_response(dataset):
    parameters = Constructor.ds_list_payload(ds=dataset)
    pytest.response = DsList.post(parameters)


@when(parsers.cfparse('ds_list request with "{smpcnt:String}" parameter is send', extra_types=EXTRA_STRING_TYPES))
def ds_list_response(dataset, smpcnt):
    parameters = Constructor.ds_list_payload(ds=dataset, smpcnt=smpcnt)
    pytest.response = DsList.post(parameters)


@then(parsers.cfparse('job_status should be "Done"', extra_types=EXTRA_STRING_TYPES),target_fixture='job_status')
def job_status():
    task_id = pytest.response.json()['task_id']
    response = ''
    for i in range(10):
        response = JobStatus.post({'task': task_id})
        if False not in response.json():
            break
        time.sleep(1)
    for element in response.json():
        if type(element) is str:
            assert element == 'Done'
    return response


@then(parsers.cfparse('number of samples should be equal "{number:String}"', extra_types=EXTRA_STRING_TYPES))
def ds_list_response(number, job_status):
    for element in job_status.json():
        if type(element) is object:
            assert len(element["samples"]) == number
