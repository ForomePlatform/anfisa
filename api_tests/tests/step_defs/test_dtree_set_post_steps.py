import pytest
from jsonschema.validators import validate
from pytest_bdd import scenarios, parsers, when, then, given

from lib.api.dtree_set_api import DtreeSet
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from lib.jsonschema.common import solution_entry_schema
from lib.jsonschema.dtree_set_schema import dtree_point_descriptor, condition_discriptor_enum, \
    condition_descriptor_numeric, condition_discriptor_func
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

scenarios('../features/dtree_set-post.feature')


@when(parsers.cfparse('dtree_set request with "{ds:String}" and "{code_name:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES))
def dtree_set_response(ds, code_name):
    if ds == 'xl Dataset' or ds == 'ws Dataset':
        ds = pytest.dataset
    parameters = Constructor.dtree_set_payload(ds=ds, code=code_name)
    pytest.response = DtreeSet.post(parameters)
    return pytest.response


@when(parsers.cfparse(
    'dtree_set request with "{ds:String}", "{code_name:String}", "{instr:String}" parameters is send',
    extra_types=EXTRA_STRING_TYPES))
def dtree_set_response(ds, code_name, instr, dataset, unique_name):
    if ds == 'xl Dataset' or ds == 'ws Dataset':
        ds = dataset
    instr = '["DTREE","%(instr)s","%(dtree)s"]' % {'dtree': unique_name, 'instr': instr}
    parameters = Constructor.dtree_set_payload(ds=ds, code=code_name, instr=instr)
    print('parameters', parameters)
    pytest.response = DtreeSet.post(parameters)
    return pytest.response


@then(parsers.cfparse('response body "{property_name:String}" "{schema_name:String}" schemas should be valid',
                      extra_types=EXTRA_STRING_TYPES))
def assert_stat_list_schemas(property_name, schema_name):
    for element in pytest.response.json()[property_name]:
        match schema_name:
            case 'dtree_point_descriptor':
                validate(element, dtree_point_descriptor)
            case 'solution_entry':
                validate(element, solution_entry_schema)


@then(parsers.cfparse('response body "{property_name:String}" condition_descriptor schemas should be valid',
                      extra_types=EXTRA_STRING_TYPES))
def assert_stat_list_schemas(property_name):
    for item in pytest.response.json()[property_name].items():
        match item[0]:
            case 'enum':
                validate(item, condition_discriptor_enum)
            case 'numeric':
                validate(item, condition_descriptor_numeric)
            case 'func':
                validate(item, condition_discriptor_func)


@then(parsers.cfparse('created dtree should be present in dtree list for selected dataset'))
def assert_dtree_presence(dataset, unique_name):
    parameters = Constructor.dtree_set_payload(ds=dataset, code=Generator.code('valid'))
    response_json = DtreeSet.post(parameters).json()
    dtree_list = []
    for dtree in response_json["dtree-list"]:
        dtree_list.append(dtree["name"])
    assert unique_name in dtree_list
