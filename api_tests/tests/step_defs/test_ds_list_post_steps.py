import pytest
import time
from pytest_bdd import scenarios, when, parsers, then

from jsonschema import validate
from lib.api.ds_list_api import DsList
from lib.api.job_status_api import JobStatus
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from lib.jsonschema.common import records_descriptor_schema
from tests.helpers.constructors import Constructor

scenarios('../features/ds_list-post.feature')


@when(parsers.cfparse('ds_list request with "{ds:String}" parameter is send', extra_types=EXTRA_STRING_TYPES))
def ds_list_response(ds):
    if ds == 'xl Dataset with > 150 records':
        ds = pytest.dataset
    parameters = Constructor.ds_list_payload(ds=ds)
    pytest.response = DsList.post(parameters)


@when(parsers.cfparse('ds_list request with "xl Dataset with > 150 records" and "{smpcnt:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES))
def ds_list_response(dataset, smpcnt):
    parameters = Constructor.ds_list_payload(ds=dataset, smpcnt=smpcnt)
    pytest.response = DsList.post(parameters)


@then(parsers.cfparse('job_status should be "Done"', extra_types=EXTRA_STRING_TYPES),
      target_fixture='job_status_response')
def job_status_response():
    task_id = pytest.response.json()['task_id']
    response = ''
    for i in range(360):
        response = JobStatus.post({'task': task_id})
        if False not in response.json():
            break
        time.sleep(1)
    for element in response.json():
        if type(element) is str:
            assert element == 'Done'
    return response


@then(parsers.cfparse('number of samples should be equal "{number:String}"', extra_types=EXTRA_STRING_TYPES))
def assert_number_of_samples(number, job_status_response):
    for element in job_status_response.json():
        if type(element) is object:
            assert len(element["samples"]) == number


@then(parsers.cfparse('job_status response body records schema should be valid'))
def check_records_schema(job_status_response):
    for element in job_status_response.json():
        if type(element) is object:
            validate(element.json(), records_descriptor_schema)
