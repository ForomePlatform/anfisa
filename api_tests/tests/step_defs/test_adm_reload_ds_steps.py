import pytest
from pytest_bdd import scenarios, parsers, when, then
from lib.api.adm_reload_ds_api import AdmReloadDs
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

scenarios('../features/adm_reload_ds-post.feature')


@when(parsers.cfparse('adm_reload_ds request with "ds" parameter is send', extra_types=EXTRA_STRING_TYPES),
      target_fixture='adm_reload_ds_response')
def adm_reload_ds_response(dataset):
    parameters = Constructor.adm_reload_ds(ds=dataset)
    pytest.response = AdmReloadDs.post(parameters)
    return pytest.response


@when(parsers.cfparse('adm_reload_ds request with incorrect {ds:String} parameter is send',
                      extra_types=EXTRA_STRING_TYPES))
def adm_reload_ds_response(ds):
    parameters = Constructor.adm_reload_ds(ds=ds)
    pytest.response = AdmReloadDs.post(parameters)
    return pytest.response

