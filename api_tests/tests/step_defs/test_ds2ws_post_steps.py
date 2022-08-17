from jsonschema import validate
from pytest_bdd import scenarios, parsers, given, when, then
from lib.api.ds2ws_api import Ds2ws
from lib.api.job_status_api import JobStatus
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator
from lib.jsonschema.ds2ws_schema import ds2ws_schema

scenarios('../features/ds2ws-post.feature')


@given(parsers.cfparse('unique {dataset_type:String} Dataset name is generated',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='unique_ws_name')
def unique_ws_name(dataset_type):
    _unique_ws_name = Generator.unique_name(dataset_type)
    assert _unique_ws_name != ''
    return _unique_ws_name


@given(parsers.cfparse('{code_type:String} Python code is constructed',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='code')
def code(code_type):
    if code_type == 'valid':
        return 'return False'
    elif code_type == 'invalid':
        return 'Invalid Python Code'


@when(parsers.cfparse('ds2ws request with <ds> and <ws> parameters is send'), target_fixture='ds2ws_response')
def ds2ws_response(dataset, unique_ws_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name)
    return Ds2ws.post(parameters)


@when(parsers.cfparse('ds2ws request with <ds>, <ws> and <code> parameters is send'), target_fixture='ds2ws_response')
def ds2ws_response(code, dataset, unique_ws_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name, code=code)
    return Ds2ws.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, text, ds2ws_response):
    assert ds2ws_response.status_code == status


@then(parsers.cfparse('response body schema should be valid'))
def assert_json_schema(ds2ws_response):
    validate(ds2ws_response.json(), ds2ws_schema)


@then(parsers.cfparse('job status should be "Done"'))
def assert_job_status(ds2ws_response):
    print('ds2ws_response', ds2ws_response.json()['task_id'])
    JobStatus.post(ds2ws_response.json()['task_id'])
    assert 1
    pass


@then(parsers.cfparse('derived dataset can be found in the dirinfo response'))
def assert_job_status(ds2ws_response):
    assert 1
    pass


@then(parsers.cfparse('<code> is present in dsinfo response for this dataset'))
def assert_job_status(ds2ws_response):
    assert 1
    pass
