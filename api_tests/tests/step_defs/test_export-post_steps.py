import pytest
from pytest_bdd import scenarios, parsers, when
from lib.api.export_api import Export
from tests.helpers.constructors import Constructor

scenarios('../features/export-post.feature')


@when(parsers.cfparse('"export" request with ds and empty conditions parameters is send'))
def export_response(dataset):
    parameters = Constructor.export_payload(ds=dataset, conditions='[]')
    pytest.response = Export.post(parameters)
    return pytest.response
