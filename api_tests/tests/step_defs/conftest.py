import json
import pytest
import time
from lib.api.adm_drop_ds_api import AdmDropDs
from lib.api.dirinfo_api import DirInfo
from tests.helpers.generators import testDataPrefix, Generator
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from pytest_bdd import parsers, given
from lib.api.ds2ws_api import Ds2ws
from lib.api.job_status_api import JobStatus
from tests.helpers.constructors import Constructor


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


@pytest.fixture
def xl_dataset():
    _dataset = ''
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        if value['kind'] == 'xl':
            _dataset = value['name']
            break
    assert _dataset != ''
    return _dataset


# Shared Given Steps
@given('I do something', target_fixture='ddg_home')
def i_do_something(fixture_function):
    print('i_do_something')


def successful_string_to_bool(successful):
    if successful == "successful":
        return True
    else:
        return False


def ds_creation_status(task_id):
    parameters = {'task': task_id}
    job_status_response = JobStatus.post(parameters)
    for i in range(10):
        if job_status_response.json()[1] == 'Done':
            break
        else:
            time.sleep(1)
            job_status_response = JobStatus.post(parameters)
            continue
    return job_status_response.json()[1]


def derive_ws(xl_dataset):
    # Deriving ws dataset
    unique_ws_name = Generator.unique_name('ws')
    parameters = Constructor.ds2ws_payload(ds=xl_dataset, ws=unique_ws_name, code='return False')
    response = Ds2ws.post(parameters)

    # Checking creation
    assert ds_creation_status(response.json()['task_id']) == 'Done'
    return unique_ws_name


@given(
    parsers.cfparse('{dataset_type:String} Dataset is uploaded and processed by the system',
                    extra_types=EXTRA_STRING_TYPES), target_fixture='dataset')
def dataset(dataset_type, xl_dataset):
    if dataset_type == 'xl':
        return xl_dataset
    elif dataset_type == 'ws':
        return derive_ws(xl_dataset)
