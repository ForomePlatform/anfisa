import json
import time

import pytest
from pytest_bdd import scenarios, parsers, when, then

from lib.api.dirinfo_api import DirInfo
from lib.api.ds2ws_api import Ds2ws
from lib.api.dsinfo_api import Dsinfo
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ds2ws-post.feature')


@when(parsers.cfparse('ds2ws request with "ds", "code" and "{ws:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, code, ws):
    if ws == 'unique_ws_Dataset_name':
        ws = pytest.unique_name
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=ws, code=code)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@when(parsers.cfparse('ds2ws request with "{ds:String}" and "{ws:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='ds2ws_response')
def ds2ws_response(dataset, ds, ws):
    if ds == 'xl Dataset' or ds == 'xl Dataset with > 9000 records':
        ds = dataset
    if ws == 'unique_ws_Dataset_name':
        ws = pytest.unique_name
    parameters = Constructor.ds2ws_payload(ds=ds, ws=ws)
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


@then(parsers.cfparse('derived dataset can be found in the dirinfo response'))
def assert_code_presence(unique_name):
    time.sleep(1)
    response = DirInfo.get()
    ds_dict = json.loads(response.content)["ds-dict"]
    print('DirInfo response', response.text)
    assert unique_name in ds_dict


@then(parsers.cfparse('"code" is present in dsinfo response for derived dataset'))
def assert_job_status(unique_name, code):
    time.sleep(1)
    response = Dsinfo.get({'ds': unique_name})
    print("DsInfo response", response.text)
    assert response.json()['receipts'][0]['dtree-code'] == code
