import pytest
from jsonschema.validators import validate
from pytest_bdd import when, parsers, scenarios, then

from lib.api.dtree_stat_api import DtreeStat
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from lib.jsonschema.common import enum_stat_list, numeric_stat_list, func_stat_list
from tests.helpers.constructors import Constructor

scenarios('../features/dtree_stat-post.feature')


@when(parsers.cfparse(
    'dtree_stat request with {ds:String}, {code:String}, {no:String} and {tm:String} parameters is send',
    extra_types=EXTRA_STRING_TYPES), target_fixture='dtree_stat')
def dtree_stat(dataset, ds, code, no, tm):
    ds_name = dataset if ds == 'xl Dataset' else ds
    parameters = Constructor.dtree_stat_payload(ds=ds_name, code=code, no=no, tm=tm)
    pytest.response = DtreeStat.post(parameters)
    return pytest.response


@when(parsers.cfparse(
    'dtree_stat request with {ds:String}, {no:String} and {tm:String} parameters is send',
    extra_types=EXTRA_STRING_TYPES), target_fixture='dtree_stat')
def dtree_stat(dataset, ds, no, tm):
    ds_name = dataset if ds == 'xl Dataset' else ds
    parameters = Constructor.dtree_stat_payload(ds=ds_name, no=no, tm=tm)
    pytest.response = DtreeStat.post(parameters)
    return pytest.response


@then(parsers.cfparse('response body stat-list schemas should be valid'))
def assert_stat_list_schemas(dtree_stat):
    for element in dtree_stat.json()['stat-list']:
        print(element,'\n',element['kind'])
        match element['kind']:
            case 'enum':
                validate(element, enum_stat_list)
            case 'numeric':
                print('numeric\n')
                validate(element, numeric_stat_list)
            case 'func':
                validate(element, func_stat_list)
                print('func\n')
