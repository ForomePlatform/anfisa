from jsonschema import validate
from pytest_bdd import scenarios, parsers, given, when, then
from lib.api.ds2ws_api import Ds2ws
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


@when(parsers.cfparse('ds2ws request with ds and ws parameters is send'), target_fixture='ds2ws_response')
def ds2ws_response(dataset, unique_ws_name):
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name)
    return Ds2ws.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, text, ds2ws_response):
    assert ds2ws_response.status_code == status


@then(parsers.cfparse('response body schema should be valid'))
def assert_json_schema(ds2ws_response):
    validate(ds2ws_response.json(), ds2ws_schema)
