import pytest
from pytest_bdd import when, scenarios, parsers
from lib.api.csv_export_api import CsvExport
from tests.helpers.constructors import Constructor

scenarios('../features/csv_export-post.feature')


@when(parsers.cfparse('csv export with "ds" and "schema" parameters is send'), target_fixture='csv_export_response')
def csv_export_response(dataset):
    parameters = Constructor.csv_export_payload(ds=dataset,schema='csv')
    pytest.response = CsvExport.post(parameters)
