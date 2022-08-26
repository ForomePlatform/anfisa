import pytest
from pytest_bdd import scenarios, parsers, when, given, then

from lib.api.ws_tags_api import WsTags
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

scenarios('../features/ws_tags-post.feature')


@given(parsers.cfparse('unique tag name is prepared',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='tag')
def tag():
    _unique_tag_name = Generator.unique_name('tag')
    assert _unique_tag_name != ''
    return _unique_tag_name


@when(parsers.cfparse('ws_tags request with "{ws:String}" and "{rec:String}" is send', extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(dataset, ws_less_9000_rec, ws, rec):
    if ws == 'generated ws':
        ws = ws_less_9000_rec
    elif ws == 'xl Dataset':
        ws = dataset
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec)
    pytest.response = WsTags.post(parameters)


@when(parsers.cfparse('ws_tags request with correct "{ws:String}", "{rec:String}" and "{tag:String}" is send',
                      extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(dataset, ws_less_9000_rec, ws, rec, tag):
    print('time to debug')
    if ws == 'ws Dataset':
        print('in ws Dataset')
        ws = ws_less_9000_rec
        print(ws)
    elif ws == 'xl Dataset':
        ws = dataset
    #tag = '{"%(tag)s": true}' % {'tag': tag}

    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec, tags=tag)
    print('parameters', parameters)
    pytest.response = WsTags.post(parameters)


@then(parsers.cfparse('response body "{property_name:String}" list should include "tag"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_status(property_name, tag):
    assert tag in pytest.response.json()[property_name]


@then(parsers.cfparse('response body "rec-tags" should include "tag object"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_status(tag):
    assert pytest.response.json()["rec-tags"] == '{"%(tag)s": true}' % {'tag': tag}
