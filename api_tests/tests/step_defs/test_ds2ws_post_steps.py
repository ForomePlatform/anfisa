import json
from jsonschema import validate
from pytest_bdd import scenarios, parsers, given, when, then
from lib.api.ds2ws_api import Ds2ws
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_INT_TYPES
from lib.api.dirinfo_api import DirInfo
from tests.helpers.generators import Generator
from lib.jsonschema.ds2ws_schema import ds2ws_schema

scenarios('../features/ds2ws-post.feature')


@given(
    parsers.cfparse('{dataset_type:String} Dataset is uploaded and processed by the system',
                    extra_types=EXTRA_STRING_TYPES), target_fixture='dataset')
def dataset(dataset_type):
    global _dataset
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        if value['kind'] == dataset_type:
            _dataset = value['name']
            break
    assert _dataset != ''
    return _dataset


@given(parsers.cfparse('unique {dataset_type:String} Dataset name is generated',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='unique_ws_name')
def unique_ws_name(dataset_type):
    _unique_ws_name = Generator.unique_name(dataset_type)
    assert _unique_ws_name != ''
    return _unique_ws_name


@when(parsers.cfparse('ds2ws request with ds and ws parameters is send'), target_fixture='ds2ws_response')
def ds2ws_response(dataset, unique_ws_name):
    parameters = {
        'ds': dataset,
        'ws': unique_ws_name,
        'code': '',
        'conditions': '',
        'filter': '',
        'dtree': '',
        'force': '',
    }
    return Ds2ws.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} OK', extra_types=EXTRA_INT_TYPES))
def assert_status(status, ds2ws_response):
    assert ds2ws_response.status_code == status


@then(parsers.cfparse('response body schema should be valid'))
def assert_json_schema(ds2ws_response):
    validate(ds2ws_response.json(), ds2ws_schema)
