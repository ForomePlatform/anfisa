import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.defaults_api import Defaults
from tests.helpers.constructors import Constructor

scenarios('../features/defaults-post.feature')


@when(parsers.cfparse('"defaults" request with "ds" parameter is send'))
def defaults_response(dataset):
    parameters = Constructor.defaults_payload(ds=dataset)
    pytest.response = Defaults.post(parameters)
    return pytest.response
