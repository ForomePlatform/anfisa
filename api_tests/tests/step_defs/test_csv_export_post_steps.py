import pytest
from pytest_bdd import when, scenarios, parsers, given, then
from lib.api.csv_export_api import CsvExport
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator
from tests.step_defs.conftest import derive_ws

scenarios('../features/csv_export-post.feature')



@when(parsers.cfparse('csv_export request with "ds" and "schema" parameters is send'))
def csv_export_response(dataset):
    parameters = Constructor.csv_export_payload(ds=dataset, schema='csv')
    pytest.response = CsvExport.post(parameters)


@when(parsers.cfparse('csv_export request with "schema" and "ds" parameters is send'))
def csv_export_response(ws_less_9000_rec):
    parameters = Constructor.csv_export_payload(ds=ws_less_9000_rec, schema='csv')
    pytest.response = CsvExport.post(parameters)


@when(parsers.cfparse('csv_export request with "{ds:String}" and "{schema:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES))
def csv_export_response(dataset, ws_less_9000_rec, ds, schema):
    if ds == 'xl Dataset':
        ds = dataset
    elif ds == 'ws with < 9000 records':
        ds = ws_less_9000_rec
    parameters = Constructor.csv_export_payload(ds=ds, schema=schema)
    pytest.response = CsvExport.post(parameters)


@then(parsers.cfparse('response body should match expected data for "{request_name:String}" request',
                      extra_types=EXTRA_STRING_TYPES))
def assert_csv_data(request_name, dataset):
    with open(f'tests/test_data/{dataset}/ws_callers_in_GATK_HOMOZYGOUS/{request_name}', encoding="utf8") as f:
        expected_data = f.read()
    assert expected_data == pytest.response.text.replace("\r", "")
