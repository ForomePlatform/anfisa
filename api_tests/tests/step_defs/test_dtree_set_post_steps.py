import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.dtree_set_api import DtreeSet
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/dtree_set-post.feature')


@when(parsers.cfparse('dtree_set request with correct "{ds:String}" and "{code:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES))
def ds2ws_response(ds, code, dataset):
    if ds == 'xl Dataset':
        ds = dataset
    parameters = Constructor.dtree_set_payload(ds=ds, code=code)
    pytest.response = DtreeSet.post(parameters)
    return pytest.response
