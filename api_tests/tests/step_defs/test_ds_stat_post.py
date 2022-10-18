import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.ds_stat_api import DsStat
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ds_stat-post.feature')


@when(parsers.cfparse('ds_stat request with "{ds:String}" parameter is send',
                      extra_types=EXTRA_STRING_TYPES))
def ds_stat_response(ds):
    if ds == 'xl Dataset' or ds == 'ws Dataset':
        ds = pytest.dataset
    parameters = Constructor.ds_stat_payload(ds=ds)
    pytest.response = DsStat.post(parameters)
