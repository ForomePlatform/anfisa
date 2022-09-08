import pytest
from pytest_bdd import scenarios, parsers, when, given

from lib.api.tag_select_api import TagSelect
from lib.api.ws_tags_api import WsTags
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator
from tests.step_defs.conftest import derive_ws, prepare_filter

scenarios('../features/tag_select-get.feature')


@given(parsers.cfparse('another ws Dataset with < 9000 records is derived'), target_fixture='another_derived_ws')
def another_derived_ws(dataset):
    code = prepare_filter(dataset)
    return derive_ws(dataset, code)


@given(parsers.cfparse('"{tag_type:String}" is created for "{rec:String}" record of ws dataset',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='tag_creation')
def tag_creation(tag_type, rec, ws_less_9000_rec, unique_name):
    tag_object = Generator.tag(unique_name, tag_type)
    parameters = Constructor.ws_tags_payload(ds=ws_less_9000_rec, rec=rec, tags=tag_object)
    return WsTags.post(parameters)


@when(parsers.cfparse(
    'tag_select request with "{ds:String}" parameter is send', extra_types=EXTRA_STRING_TYPES))
def tag_select(dataset, ds):
    if (ds == 'ws Dataset') or (ds == 'xl Dataset'):
        ds = dataset
    parameters = Constructor.tag_select_payload(ds=ds)
    pytest.response = TagSelect.get(parameters)
    return pytest.response


@when(parsers.cfparse(
    'tag_select request with second ws dataset as "ds" is send', extra_types=EXTRA_STRING_TYPES))
def tag_select(another_derived_ws):
    parameters = Constructor.tag_select_payload(ds=another_derived_ws)
    pytest.response = TagSelect.get(parameters)
    return pytest.response


@when(parsers.cfparse(
    'tag_select request with specified "ds" parameter is send'))
def tag_select(derived_ws):
    parameters = Constructor.tag_select_payload(ds=derived_ws)
    pytest.response = TagSelect.get(parameters)
    return pytest.response
