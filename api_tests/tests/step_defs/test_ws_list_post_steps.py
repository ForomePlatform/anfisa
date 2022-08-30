import pytest
from pytest_bdd import scenarios, when, parsers

from lib.api.ws_list_api import WsList
from tests.helpers.constructors import Constructor

scenarios('../features/ws_list-post.feature')


@when(parsers.cfparse('ws_list request with correct "ds" parameter is send'))
def dtree_stat(ws_less_9000_rec):
    parameters = Constructor.ws_list_payload(ds=ws_less_9000_rec)
    pytest.response = WsList.post(parameters)
    return pytest.response
