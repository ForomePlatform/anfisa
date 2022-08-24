import json
import pytest
import time
from lib.api.adm_drop_ds_api import AdmDropDs
from lib.api.dirinfo_api import DirInfo
from lib.api.dsinfo_api import Dsinfo
from tests.helpers.generators import testDataPrefix, Generator
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from jsonschema import validate
from pytest_bdd import parsers, given, then
from lib.api.ds2ws_api import Ds2ws
from lib.api.job_status_api import JobStatus
from tests.helpers.constructors import Constructor
from lib.jsonschema.ds2ws_schema import ds2ws_schema
from lib.jsonschema.dsinfo_schema import dsinfo_schema
from lib.jsonschema.dtree_check_schema import dtree_check_schema


# Hooks
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f'Step failed: {step}')


def pytest_bdd_after_scenario():
    ws_to_drop = []
    response = DirInfo.get()
    ds_dict = json.loads(response.content)["ds-dict"]
    for value in ds_dict.values():
        try:
            if testDataPrefix + 'ws' in value['name']:
                ws_to_drop.append(value['name'])
        except ValueError:
            continue
        except TypeError:
            continue
    for wsDataset in ws_to_drop:
        time.sleep(1)
        AdmDropDs.post({'ds': wsDataset})


# Fixtures
@pytest.fixture
def fixture_function():
    print('fixture_function')


# Shared Given Steps
@given('I do something', target_fixture='ddg_home')
def i_do_something(fixture_function):
    print('i_do_something')


def successful_string_to_bool(successful):
    if successful == "successful":
        return True
    else:
        return False


def number_of_ds_records(ds_name):
    response = Dsinfo.get({'ds': ds_name})
    return response.json()['total']


def xl_dataset(required_records=0):
    _dataset = ''
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        if (value['kind'] == 'xl') and (number_of_ds_records(value['name']) > required_records):
            _dataset = value['name']
            break
    assert _dataset != ''
    return _dataset


def ds_creation_status(task_id):
    parameters = {'task': task_id}
    job_status_response = JobStatus.post(parameters)
    for i in range(10):
        if (job_status_response.json()[1] == 'Done') or (job_status_response.json()[0] is None):
            break
        else:
            time.sleep(1)
            job_status_response = JobStatus.post(parameters)
            continue
    return job_status_response.json()[1]


def derive_ws(dataset):
    # Deriving ws dataset
    unique_ws_name = Generator.unique_name('ws')
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name, code='return False')
    response = Ds2ws.post(parameters)

    # Checking creation
    assert ds_creation_status(response.json()['task_id']) == 'Done'
    return unique_ws_name


@given(
    parsers.cfparse('{dataset_type:String} is uploaded and processed by the system',
                    extra_types=EXTRA_STRING_TYPES), target_fixture='dataset')
def dataset(dataset_type):
    match dataset_type:
        case 'xl Dataset':
            return xl_dataset()
        case 'xl Dataset with > 9000 records':
            return xl_dataset(9000)
        case 'ws Dataset':
            return derive_ws(xl_dataset())
        case other:
            return xl_dataset()


@then(parsers.cfparse('response body schema should be valid by "{schema:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_json_schema(schema):
    print(schema)
    match schema:
        case 'dsinfo_schema':
            validate(pytest.response.json(), dsinfo_schema)
        case 'dtree_check_schema':
            validate(pytest.response.json(), dtree_check_schema)
        case 'ds2ws_schema':
            validate(pytest.response.json(), ds2ws_schema)
        case _:
            print(f"Sorry, I couldn't understand {schema!r}")


@then(parsers.cfparse('response body "{key:String}" should be equal {value:String}', extra_types=EXTRA_STRING_TYPES))
def assert_response_code(key, value):
    response_json = json.loads(pytest.response.text)
    assert response_json[key] == value


@then(parsers.cfparse('response body should contain "{error_message:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(error_message):
    assert error_message in pytest.response.text


@then(parsers.cfparse('response body should be equal "{body:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(body):
    assert pytest.response.text == f'"{body}"'


@then(parsers.cfparse('response status should be {status:Number} {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, text):
    assert pytest.response.status_code == status


@given(parsers.cfparse('unique {dataset_type:String} Dataset name is generated',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='unique_ds_name')
def unique_ds_name(dataset_type):
    _unique_ds_name = Generator.unique_name(dataset_type)
    assert _unique_ds_name != ''
    return _unique_ds_name


@then(parsers.cfparse('job status should be {status:String}', extra_types=EXTRA_STRING_TYPES))
def assert_job_status(status):
    assert status in ds_creation_status(pytest.response.json()['task_id'])


@given(parsers.cfparse('{code_type:String} Python code is constructed',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='code')
def code(code_type):
    return Generator.code(code_type)
