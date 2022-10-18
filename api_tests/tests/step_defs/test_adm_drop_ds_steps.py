import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.adm_drop_ds_api import AdmDropDs
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/adm_drop_ds-post.feature')


@when(parsers.cfparse('adm_drop_ds requests with "{ds:String}" parameter is send', EXTRA_STRING_TYPES))
def adm_drop_ds_response(dataset, ds):
    if ds == 'ws Dataset with <test> in the name':
        ds = dataset
    parameters = Constructor.arm_drop_ds_payload(ds=ds)
    pytest.response = AdmDropDs.post(parameters)
    return pytest.response

