import json

import pytest
from pytest_bdd import scenarios, parsers, then, when
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from lib.api.dsinfo_api import Dsinfo

scenarios('../features/dsinfo-get.feature')


@when(parsers.cfparse('dsinfo request is send with parameters: "{parameters:String}"',
                      extra_types=EXTRA_STRING_TYPES), target_fixture='dsinfo_response')
def dsinfo_response(parameters):
    parameters = json.loads(parameters)
    pytest.response = Dsinfo.get(parameters)
    return pytest.response


@then(parsers.cfparse('I see a "{error_message:String}" error message in response', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(dsinfo_response, error_message):
    assert error_message in dsinfo_response.text
