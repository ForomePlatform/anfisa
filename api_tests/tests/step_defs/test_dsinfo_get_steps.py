import json
from pytest_bdd import scenarios, parsers, given, then, when
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from lib.api.dsinfo_api import Dsinfo
from tests.step_defs.conftest import successful_string_to_bool
from lib.jsonschema.dsinfo_schema import dsinfo_schema
from jsonschema import validate

dsinfo = Dsinfo()

scenarios('../features/dsinfo-get.feature')


@when(parsers.cfparse('I send get dsinfo request with parameters: "{parameters:String}" ({successful:String})',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='dsinfo_response')
def dsinfo_response(parameters, successful):
    parameters = json.loads(parameters)
    successful = successful_string_to_bool(successful)
    return dsinfo.get(parameters, successful)


@then(parsers.cfparse('I validate the response by schema'))
def dsinfo_response_validate(dsinfo_response):
    validate(dsinfo_response.json(), dsinfo_schema)


@then(parsers.cfparse('I see a "name" key equal to "{name:String}" text in response',
                      extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_message(dsinfo_response, name):
    response = dsinfo_response.json()
    assert response["name"] == name


@then(parsers.cfparse('I see a "{error_message:String}" error message in response', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(dsinfo_response, error_message):
    assert error_message in dsinfo_response.text
