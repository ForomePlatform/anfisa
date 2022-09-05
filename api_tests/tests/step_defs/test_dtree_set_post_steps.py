import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.dtree_set_api import DtreeSet
from tests.helpers.constructors import Constructor

scenarios('../features/dtree_set-post.feature')


@when(parsers.cfparse('dtree_set request with correct "ds" and "code" parameters is send',))
def ds2ws_response(dataset, code, unique_ds_name):
    parameters = Constructor.dtree_set_payload(ds=dataset, ws=unique_ds_name, code=code)
    pytest.response = DtreeSet.post(parameters)
    return pytest.response