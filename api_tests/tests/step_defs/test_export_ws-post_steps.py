import pytest
from pytest_bdd import scenarios, parsers, when
from lib.api.export_ws_api import ExportWs
from tests.helpers.constructors import Constructor

scenarios('../features/export_ws-post.feature')


@when(parsers.cfparse('"export_ws" request with "ds" parameter is send'))
def export_ws_response(dataset):
    parameters = Constructor.export_ws_payload(ds=dataset)
    pytest.response = ExportWs.post(parameters)
    return pytest.response