import pytest
from pytest_bdd import scenarios, when, parsers

from lib.api.ws_list_api import WsList
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ws_list-post.feature')


@when(parsers.cfparse('ws_list request with "{ds:String}" parameter is send', extra_types=EXTRA_STRING_TYPES))
def dtree_stat(dataset, ws_less_9000_rec,ds):
    if ds == 'xl Dataset':
        ds = dataset
    elif ds == 'ws Dataset with < 9000':
        ds = ws_less_9000_rec
    parameters = Constructor.ws_list_payload(ds=ds)
    pytest.response = WsList.post(parameters)
    return pytest.response
