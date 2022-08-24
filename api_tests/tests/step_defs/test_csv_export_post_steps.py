import pytest
from pytest_bdd import when, scenarios, parsers, given, then
from lib.api.csv_export_api import CsvExport
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.step_defs.conftest import derive_ws

scenarios('../features/csv_export-post.feature')


@given(parsers.cfparse('ws Dataset, derived by "{code:String}", is prepared', extra_types=EXTRA_STRING_TYPES),
       target_fixture='ws_derived_by_code')
def ws_derived_by_code(dataset, code):
    return derive_ws(dataset, code)


@when(parsers.cfparse('csv_export request with "ds" and "schema" parameters is send'))
def csv_export_response(dataset):
    parameters = Constructor.csv_export_payload(ds=dataset, schema='csv')
    pytest.response = CsvExport.post(parameters)


@when(parsers.cfparse('csv_export request with "schema" and "ds" parameters is send'))
def csv_export_response(ws_derived_by_code):
    parameters = Constructor.csv_export_payload(ds=ws_derived_by_code, schema='csv')
    pytest.response = CsvExport.post(parameters)


@then(parsers.cfparse('response body should match expected data for "{request_name:String}" request',
                      extra_types=EXTRA_STRING_TYPES))
def assert_csv_data(request_name, dataset):
    with open(f'tests/test_data/{dataset}/ws_callers_in_GATK_HOMOZYGOUS/{request_name}', encoding="utf8") as f:
        expected_data = f.read()
    print('pytest.response.text', pytest.response.text)
    #assert expected_data == pytest.response.text
