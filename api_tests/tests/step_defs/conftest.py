import json
import pytest
from csvvalidator import CSVValidator
from deepdiff import DeepDiff
from jsonschema import validate
from pytest_bdd import parsers, given, then
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from lib.jsonschema.export_ws_schema import export_ws_schema
from lib.jsonschema.common import enum_property_status_schema, numeric_property_status_schema, \
    func_property_status_schema, solution_entry_schema
from lib.jsonschema.csv_export_schema import csv_export_schema
from lib.jsonschema.defaults_schema import defaults_schema
from lib.jsonschema.ds2ws_schema import ds2ws_schema
from lib.jsonschema.ds_list_schema import ds_list_schema
from lib.jsonschema.ds_stat_schema import ds_stat_schema
from lib.jsonschema.dsinfo_schema import dsinfo_schema
from lib.jsonschema.dtree_check_schema import dtree_check_schema
from lib.jsonschema.dtree_counts_schema import dtree_counts_schema
from lib.jsonschema.dtree_set_schema import dtree_set_schema
from lib.jsonschema.dtree_stat_schema import dtree_stat_schema
from lib.jsonschema.export_schema import export_schema
from lib.jsonschema.job_status_schema import job_status_schema
from lib.jsonschema.stat_units_schema import stat_units_schema
from lib.jsonschema.tag_select_schema import tag_select_schema
from lib.jsonschema.vsetup_schema import vsetup_schema
from lib.jsonschema.ws_list_schema import ws_list_schema
from lib.jsonschema.ws_tags_schema import ws_tags_schema
from lib.jsonschema.zone_list_schema import zone_descriptor_serial, zone_descriptor_single
from tests.helpers.functions import xl_dataset, derive_ws, prepare_filter, find_dataset, ds_creation_status
from tests.helpers.generators import Generator


# Hooks
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f'Step failed: {step}')


def pytest_bdd_after_scenario():
    pass


# Fixtures
@pytest.fixture
def fixture_function():
    print('fixture_function')


# Shared Given Steps
@given('I do something', target_fixture='ddg_home')
def i_do_something(fixture_function):
    print('i_do_something')


@given(
    parsers.cfparse('"{dataset_identifier:String}" is uploaded and processed by the system',
                    extra_types=EXTRA_STRING_TYPES), target_fixture='dataset')
def dataset(dataset_identifier):
    print('\npreparing dataset..')
    match dataset_identifier:
        case 'xl Dataset':
            return xl_dataset()
        case 'xl Dataset with > 9000 records':
            return xl_dataset(9000)
        case 'xl Dataset with > 150 records':
            return xl_dataset(150)
        case 'ws Dataset' | 'ws Dataset with <test> in the name':
            return derive_ws(xl_dataset())
        case 'xl Dataset with code filter':
            xl_ds = ''
            for i in range(10):
                xl_ds = xl_dataset()
                prep_filter = prepare_filter(xl_ds)
                if prep_filter != '':
                    break
                xl_ds = ''
            assert xl_ds != ''
            return xl_ds
        case _:
            find_dataset(dataset_identifier)
            return dataset_identifier


@given(parsers.cfparse('unique "{name_type:String}" is generated',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='unique_name')
def unique_name(name_type):
    _unique_name = ''
    match name_type:
        case 'xl Dataset name':
            _unique_name = Generator.unique_name('xl')
        case 'ws Dataset name':
            _unique_name = Generator.unique_name('ws')
        case 'tag':
            _unique_name = Generator.unique_name('tag')
        case 'Dtree name':
            _unique_name = Generator.unique_name('dtree')
    assert _unique_name != ''
    return _unique_name


@given(parsers.cfparse('"{code_type:String}" Python code is constructed',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='code')
def code(code_type):
    return Generator.code(code_type)


@given(parsers.cfparse('"{code_type:String}" Python code is constructed',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='code')
def code(code_type):
    return Generator.code(code_type)


@given(parsers.cfparse('ws Dataset with < 9000 records is derived from it', extra_types=EXTRA_STRING_TYPES),
       target_fixture='ws_less_9000_rec')
def ws_less_9000_rec(dataset):
    code = prepare_filter(dataset)
    return derive_ws(dataset, code)


@given(parsers.cfparse('ws Dataset is derived from it'), target_fixture='derived_ws')
def derived_ws(dataset):
    return derive_ws(dataset)


@then(parsers.cfparse('response body "{property_name:String}" tag list should include "{tag_type:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_status(property_name, unique_name, tag_type):
    if tag_type == 'generated true Tag':
        assert unique_name in pytest.response.json()[property_name]
    elif tag_type == 'generated _note Tag':
        assert '_note' in pytest.response.json()[property_name]


@then(parsers.cfparse('job status should be "{status:String}"', extra_types=EXTRA_STRING_TYPES))
def assert_job_status(status):
    assert status in ds_creation_status(pytest.response.json()['task_id'])


@then(parsers.cfparse('response body json should match expected data for "{request_name:String}" request',
                      extra_types=EXTRA_STRING_TYPES))
def assert_test_data(request_name, dataset):
    path = f'tests/test-data/{dataset}/{request_name}.json'
    with open(path, encoding="utf8") as f:
        test_data_json = json.load(f)
    response_json = json.loads(pytest.response.text)

    print('\ntest_data_json\n', json.dumps(test_data_json, indent=4, sort_keys=True))
    print('\nresponse_json\n', json.dumps(response_json, indent=4, sort_keys=True))

    ddiff = DeepDiff(test_data_json, response_json, ignore_order=True,
                     exclude_paths={"root['rq-id']", "root['upd-time']", "root['upd-from']", "root['tags-state']",
                                    "root['op-tags']", "root['rec-tags']", "root['dtree-list']", "root['ds']"})
    print('ddiff', ddiff)

    assert ddiff == {}


@then(parsers.cfparse('response body "{property_name_1:String}" value should be equal "{property_name_2:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def determine_equality_of_properties(property_name_1, property_name_2):
    response_json = json.loads(pytest.response.text)
    # print('response_json[property_name_1]', response_json[property_name_1])
    # print('response_json[property_name_2]', response_json[property_name_2])
    assert response_json[property_name_1] == response_json[property_name_2]


@then(parsers.cfparse('response body "{property_name:String}" "{schema_name:String}" schemas should be valid',
                      extra_types=EXTRA_STRING_TYPES))
def assert_nested_schemas(property_name, schema_name):
    match schema_name:
        case 'solution_entry':
            for element in pytest.response.json()[property_name]:
                print('element', element)
                validate(element, solution_entry_schema)
        case 'descriptor':
            for element in pytest.response.json()[property_name]:
                print('element', element)
                validate(element, ws_list_schema)


@then(parsers.cfparse('response body "{property_name:String}" property_status schemas should be valid',
                      extra_types=EXTRA_STRING_TYPES))
def assert_stat_list_schemas(property_name):
    for element in pytest.response.json()[property_name]:
        match element['kind']:
            case 'enum':
                validate(element, enum_property_status_schema)
            case 'numeric':
                validate(element, numeric_property_status_schema)
            case 'func':
                validate(element, func_property_status_schema)


@then(parsers.cfparse('response body should contain "{error_message:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(error_message):
    assert error_message in pytest.response.text


@then(parsers.cfparse('response body should be equal "{body:String}"', extra_types=EXTRA_STRING_TYPES))
def dsinfo_response_error(body):
    assert pytest.response.text == f'"{body}"'


@then(parsers.cfparse('response status should be "{status:Number}" {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, text):
    assert pytest.response.status_code == status


@then(parsers.cfparse('response body "{key:String}" should be equal "{value:String}"', extra_types=EXTRA_STRING_TYPES))
def assert_response_code(key, value):
    if value[:9] == 'generated':
        value = Generator.test_data(value[10:])
    elif value[:4] == 'gen.':
        value = Generator.test_data(value[5:])
    response_json = json.loads(pytest.response.text)
    assert response_json[key] == value


@then(parsers.cfparse('response body schema should be valid by "{schema:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_json_schema(schema):
    print(schema)
    match schema:
        case 'dsinfo_schema':
            validate(pytest.response.json(), dsinfo_schema)
        case 'dtree_check_schema':
            validate(pytest.response.json(), dtree_check_schema)
        case 'ds2ws_schema':
            validate(pytest.response.json(), ds2ws_schema)
        case 'job_status_schema':
            validate(pytest.response.json(), job_status_schema)
        case 'ds_list_schema':
            validate(pytest.response.json(), ds_list_schema)
        case 'dtree_stat_schema':
            validate(pytest.response.json(), dtree_stat_schema)
        case 'dtree_set_schema':
            validate(pytest.response.json(), dtree_set_schema)
        case 'ds_stat_schema':
            validate(pytest.response.json(), ds_stat_schema)
        case 'ws_tags_schema':
            validate(pytest.response.json(), ws_tags_schema)
        case 'stat_units_schema':
            validate(pytest.response.json(), stat_units_schema)
        case 'ws_list_schema':
            validate(pytest.response.json(), ws_list_schema)
        case 'tag_select_schema':
            validate(pytest.response.json(), tag_select_schema)
        case 'zone_descriptor_serial':
            validate(pytest.response.json(), zone_descriptor_serial)
        case 'zone_descriptor_single':
            validate(pytest.response.json(), zone_descriptor_single)
        case 'defaults_schema':
            validate(pytest.response.json(), defaults_schema)
        case 'dtree_counts_schema':
            validate(pytest.response.json(), dtree_counts_schema)
        case 'export_schema':
            validate(pytest.response.json(), export_schema)
        case 'export_ws_schema':
            validate(pytest.response.json(), export_ws_schema)
        case 'vsetup_schema':
            validate(pytest.response.json(), vsetup_schema)
        case 'csv_export_schema':
            validator = CSVValidator(csv_export_schema)
            validator.add_value_check('chromosome', str)
            validator.add_value_check('variant', str)
            problems = validator.validate(pytest.response.text)
            assert len(problems) == 0
        case _:
            print(f"Sorry, I couldn't understand {schema!r}")
            raise NameError('Schema is not found')
