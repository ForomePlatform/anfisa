import json
import pytest
import time
from lib.api.adm_drop_ds_api import AdmDropDs
from lib.api.dirinfo_api import DirInfo
from tests.helpers.generators import testDataPrefix
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from pytest_bdd import  parsers, given



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

@given(
    parsers.cfparse('{dataset_type:String} Dataset is uploaded and processed by the system',
                    extra_types=EXTRA_STRING_TYPES), target_fixture='dataset')
def dataset(dataset_type):
    _dataset = ''
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        if value['kind'] == dataset_type:
            _dataset = value['name']
            break
    assert _dataset != ''
    return _dataset
