import json
from jsonschema import validate
from pytest_bdd import scenarios, parsers, when, then
from lib.api.dtree_check_api import DtreeCheck
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_INT_TYPES
from lib.jsonschema.dtree_check_schema import dtree_check_schema
from tests.helpers.constructors import Constructor

scenarios('../features/dtree_check-post.feature')


@when(parsers.cfparse('dtree_check request with {code:String} and {ds:String} is send', extra_types=EXTRA_STRING_TYPES),
      target_fixture='dtree_check_response')
def dtree_check_response(code, ds, dataset):
    dataset_name = dataset if ds == 'xl dataset' else ds
    parameters = Constructor.dtree_check_payload(ds=dataset_name, code=code)
    _response = DtreeCheck.post(parameters)
    return _response


@then(parsers.cfparse('response status should be {status:Number} OK', extra_types=EXTRA_INT_TYPES))
def assert_status(status, dtree_check_response):
    assert dtree_check_response.status_code == status


@then(parsers.cfparse('response body schema should be valid'))
def assert_json_schema(dtree_check_response):
    validate(dtree_check_response.json(), dtree_check_schema)


@then(parsers.cfparse('response body code should be equal {code:String}', extra_types=EXTRA_STRING_TYPES))
def assert_response_code(code, dtree_check_response):
    response_json = json.loads(dtree_check_response.text)
    assert response_json['code'] == code


@then(parsers.cfparse('response body error should be equal {error:String}', extra_types=EXTRA_STRING_TYPES))
def assert_json_error(error, dtree_check_response):
    response_json = json.loads(dtree_check_response.text)
    assert response_json['error'] == error


@then(parsers.cfparse('response body should contain {error:String}', extra_types=EXTRA_STRING_TYPES))
def assert_string_error(error, dtree_check_response):
    response = dtree_check_response.text
    assert error in response
