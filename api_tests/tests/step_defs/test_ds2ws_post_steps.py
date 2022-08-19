import pytest
import json
from pytest_bdd import scenarios, parsers, given, when, then
from lib.api.dirinfo_api import DirInfo
from lib.api.ds2ws_api import Ds2ws
from lib.api.dsinfo_api import Dsinfo
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator
from tests.step_defs.conftest import ds_creation_status

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
    return Generator.code(code_type)


@when(parsers.cfparse('ds2ws request with "ds" and "ws" parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, unique_ws_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with "ds", "code" and {ws:String} parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, ws, code):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=ws, code=code)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with "ds", "ws" and "code" parameters is send'), target_fixture='ds2ws_response')
def ds2ws_response(code, dataset, unique_ws_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name, code=code)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with {ds:String} and {ws:String} parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, ds, ws):
    ds_name = dataset if ds == 'xl Dataset' else ds
    parameters = Constructor.ds2ws_payload(ds=ds_name, ws=ws)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@then(parsers.cfparse('job status should be {status:String}', extra_types=EXTRA_STRING_TYPES))
def assert_job_status(ds2ws_response, status):
    assert status in ds_creation_status(ds2ws_response.json()['task_id'])


@then(parsers.cfparse('derived dataset can be found in the dirinfo response'))
def assert_code_presence(unique_ws_name):
    response = DirInfo.get()
    ds_dict = json.loads(response.content)["ds-dict"]
    assert unique_ws_name in ds_dict


@then(parsers.cfparse('<code> is present in dsinfo response for derived dataset'))
def assert_job_status(unique_ws_name, code):
    response = Dsinfo.get({'ds': unique_ws_name})
    assert response.json()['receipts'][0]['dtree-code'] == code
