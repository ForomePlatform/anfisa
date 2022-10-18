import pytest
from pytest_bdd import when, scenarios, parsers, then
from lib.api.csv_export_api import CsvExport
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/csv_export-post.feature')


@when(parsers.cfparse('csv_export request with "{ds:String}" and "{schema:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES))
def csv_export_response(ds, schema):
    if ds == 'xl Dataset' or ds == 'ws Dataset':
        ds = pytest.dataset
    elif ds == 'ws with < 9000 records':
        ds = pytest.ws_less_9000_rec
    parameters = Constructor.csv_export_payload(ds=ds, schema=schema)
    pytest.response = CsvExport.post(parameters)


@then(parsers.cfparse('response body should match expected data for "{request_name:String}" request',
                      extra_types=EXTRA_STRING_TYPES))
def assert_csv_data(dataset, request_name):
    with open(f'tests/test-data/{dataset}/{request_name}', encoding="utf8") as f:
        expected_data = f.read()
    assert expected_data == pytest.response.text.replace("\r", "")