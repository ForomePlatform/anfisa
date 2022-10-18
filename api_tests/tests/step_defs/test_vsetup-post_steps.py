import pytest
from pytest_bdd import scenarios, parsers, when
from lib.api.vsetup_api import Vsetup
from tests.helpers.constructors import Constructor

scenarios('../features/vsetup-post.feature')


@when(parsers.cfparse('"vsetup" request with "ds" parameter is send'))
def vsetup_response(dataset):
    parameters = Constructor.vsetup_payload(ds=dataset)
    pytest.response = Vsetup.post(parameters)
    return pytest.response
