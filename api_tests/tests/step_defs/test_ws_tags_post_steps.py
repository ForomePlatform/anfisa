import json
import pytest
from pytest_bdd import scenarios, parsers, when, given, then

from lib.api.tag_select_api import TagSelect
from lib.api.ws_tags_api import WsTags
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

scenarios('../features/ws_tags-post.feature')


@given(parsers.cfparse('unique tag is prepared',
                       extra_types=EXTRA_STRING_TYPES), target_fixture='unique_tag')
def unique_tag():
    _unique_tag_name = Generator.unique_name('tag')
    assert _unique_tag_name != ''
    return _unique_tag_name


@when(parsers.cfparse('ws_tags request with "{ws:String}" and "{rec:String}" is send', extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(dataset, ws_less_9000_rec, ws, rec):
    if ws == 'ws Dataset':
        ws = ws_less_9000_rec
    elif ws == 'xl Dataset':
        ws = dataset
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec)
    pytest.response = WsTags.post(parameters)


@when(parsers.cfparse('ws_tags request with correct "{ws:String}", "{rec:String}" and "{tag_type:String}" is send',
                      extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(dataset, ws_less_9000_rec, ws, rec, tag_type, unique_tag):
    if ws == 'ws Dataset':
        ws = ws_less_9000_rec
    elif ws == 'xl Dataset':
        ws = dataset

    tag_object = Generator.tag(unique_tag, tag_type)
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec, tags=tag_object)
    pytest.response = WsTags.post(parameters)


@then(parsers.cfparse('response body "{property_name:String}" list should include "{tag_type:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_status(property_name, unique_tag, tag_type):
    if tag_type == 'generated true Tag':
        assert unique_tag in pytest.response.json()[property_name]
    elif tag_type == 'generated _note Tag':
        assert '_note' in pytest.response.json()[property_name]


@then(parsers.cfparse('response body "rec-tags" should include "{tag_type:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_status(unique_tag, tag_type):
    if tag_type == 'generated true Tag':
        assert '{"%(tag)s": true}' % {'tag': unique_tag} == json.dumps(pytest.response.json()["rec-tags"])
    elif tag_type == 'generated _note Tag':
        assert '{"_note": "%(text)s"}' % {'text': unique_tag} == json.dumps(pytest.response.json()["rec-tags"])


@then(parsers.cfparse('tag_select response should include "{tag_type:String}"',extra_types=EXTRA_STRING_TYPES))
def assert_status(unique_tag, ws_less_9000_rec, tag_type):
    parameters = Constructor.tag_select_payload(ds=ws_less_9000_rec)
    response = TagSelect.get(parameters)

    if tag_type == 'generated true Tag':
        assert unique_tag in response.json()["tag-list"]
    elif tag_type == 'generated _note Tag':
        assert '_note' in response.json()["tag-list"]


