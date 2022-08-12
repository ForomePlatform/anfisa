import json

from jsonschema import validate
from pytest_bdd import scenarios, parsers, when, then

from lib.api.dtree_check_api import DtreeCheck
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_INT_TYPES
from lib.jsonschema.dtree_check_schema import dtree_check_schema

scenarios('../features/dtree_check-post.feature')

dataset = ''
code = ''
response = ''


@when(parsers.cfparse('dtree_check request with {code:String} is send', extra_types=EXTRA_STRING_TYPES))
def dtree_check_request(code, get_random_dataset_name):
    global response
    parameters = {
        'ds': get_random_dataset_name,
        'code': code,
    }
    response = DtreeCheck.post(parameters)


@when(parsers.cfparse('dtree_check request without code is send'))
def dtree_check_request_without_code(get_random_dataset_name):
    global response
    parameters = {
        'ds': get_random_dataset_name,
        'code': '',
    }
    response = DtreeCheck.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} OK', extra_types=EXTRA_INT_TYPES))
def assert_status(status):
    global response
    assert response.status_code == status


@then(parsers.cfparse('response body schema should be valid'))
def assert_json_schema():
    global response
    validate(response.json(), dtree_check_schema)


@then(parsers.cfparse('response body code should be equal {code:String}', extra_types=EXTRA_STRING_TYPES))
def assert_response_code(code):
    global response
    response_json = json.loads(response.text)
    assert response_json['code'] == code


@then(parsers.cfparse('response body error should be equal {error:String}', extra_types=EXTRA_STRING_TYPES))
def assert_json_error(error):
    global response
    response_json = json.loads(response.text)
    assert response_json['error'] == error


@then(parsers.cfparse('response body should contain {error:String}', extra_types=EXTRA_STRING_TYPES))
def assert_string_error(error):
    global response
    response = response.text
    assert error in response
