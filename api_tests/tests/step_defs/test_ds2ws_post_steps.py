import json

import pytest
from pytest_bdd import scenarios, parsers, when, then

from lib.api.dirinfo_api import DirInfo
from lib.api.ds2ws_api import Ds2ws
from lib.api.dsinfo_api import Dsinfo
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ds2ws-post.feature')


@when(parsers.cfparse('ds2ws request with correct "ds" and "ws" parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, unique_ds_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ds_name)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with correct "ds", "code" and "ws" parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, code, unique_ds_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ds_name, code=code)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with incorrect "ds", "code" and "{ws:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, code, ws):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=ws, code=code)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with incorrect {ds:String} and {ws:String} parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, ds, ws):
    ds_name = dataset if ds == 'xl Dataset' else ds
    parameters = Constructor.ds2ws_payload(ds=ds_name, ws=ws)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@then(parsers.cfparse('derived dataset can be found in the dirinfo response'))
def assert_code_presence(unique_ds_name):
    response = DirInfo.get()
    ds_dict = json.loads(response.content)["ds-dict"]
    assert unique_ds_name in ds_dict


@then(parsers.cfparse('"code" is present in dsinfo response for derived dataset'))
def assert_job_status(unique_ds_name, code):
    response = Dsinfo.get({'ds': unique_ds_name})
    assert response.json()['receipts'][0]['dtree-code'] == code
