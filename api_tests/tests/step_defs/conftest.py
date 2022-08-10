import json
import pytest
import time
from pytest_bdd import given
from lib.api.adm_drop_ds import Adm_drop_ds
from lib.api.dirinfo_api import DirInfo
from tests.helpers.generators import testDataPrefix

# Hooks
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f'Step failed: {step}')

def pytest_bdd_after_scenario():
    wsToDrop = []
    response = DirInfo.get()
    dsDict = json.loads(response.content)["ds-dict"]
    for value in dsDict.values():
        try: 
            if testDataPrefix + 'ws' in value['name']:
                wsToDrop.append(value['name'])
        except:
            continue
    for wsDataset in wsToDrop:
        time.sleep(1)
        Adm_drop_ds.post({'ds': wsDataset})



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
