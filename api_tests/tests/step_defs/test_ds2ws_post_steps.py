import pytest
from pytest_bdd import scenarios, parsers, given, when
from lib.api.ds2ws_api import Ds2ws
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

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
    pytest.response = Ds2ws.post(parameters)
    return pytest.response


