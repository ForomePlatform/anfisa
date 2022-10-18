import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.defaults_api import Defaults
from tests.helpers.constructors import Constructor
from lib.interfaces.interfaces import EXTRA_STRING_TYPES

scenarios('../features/defaults-post.feature')


@when(parsers.cfparse('"defaults" request with "{ds:String}" parameter is send', EXTRA_STRING_TYPES))
def defaults_response(dataset, ds):
    parameters = Constructor.defaults_payload(ds=dataset)
    pytest.response = Defaults.post(parameters)
    return pytest.response
