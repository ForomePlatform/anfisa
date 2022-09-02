import pytest
from pytest_bdd import scenarios, when, parsers

from lib.api.ds_list_api import DsList
from tests.helpers.constructors import Constructor

scenarios('../features/ds_list-post.feature')


@when(parsers.cfparse('ds_list request is send'))
def ds2ws_response(dataset):
    parameters = Constructor.ds_list_payload(ds=dataset)
    pytest.response = DsList.post(parameters)
    return pytest.response
