import json
import pytest
from pytest_bdd import scenarios, parsers, when, given, then

from lib.api.tag_select_api import TagSelect
from lib.api.ws_tags_api import WsTags
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

scenarios('../features/ws_tags-post.feature')


@when(parsers.cfparse('ws_tags request with "{ws:String}" and "{rec:String}" is send', extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(dataset, ws_less_9000_rec, ws, rec):
    if ws == 'ws Dataset':
        ws = ws_less_9000_rec
    elif ws == 'xl Dataset':
        ws = dataset
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec)
    pytest.response = WsTags.post(parameters)


@when(parsers.cfparse('ws_tags request with correct "{ws:String}", "{rec:String}", "{tag_type:String}" is send',
                      extra_types=EXTRA_STRING_TYPES))
def tag_creation(dataset, ws_less_9000_rec, ws, rec, tag_type, unique_name):
    if ws == 'ws Dataset':
        ws = ws_less_9000_rec
    elif ws == 'xl Dataset':
        ws = dataset

    tag_object = Generator.tag(unique_name, tag_type)
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec, tags=tag_object)
    pytest.response = WsTags.post(parameters)


@then(parsers.cfparse('response body "rec-tags" should include "{tag_type:String}"',
                      extra_types=EXTRA_STRING_TYPES))
def assert_status(unique_name, tag_type):
    if tag_type == 'generated true Tag':
        assert '{"%(tag)s": true}' % {'tag': unique_name} == json.dumps(pytest.response.json()["rec-tags"])
    elif tag_type == 'generated _note Tag':
        assert '{"_note": "%(text)s"}' % {'text': unique_name} == json.dumps(pytest.response.json()["rec-tags"])


@then(parsers.cfparse('tag_select response should include "{tag_type:String}"', extra_types=EXTRA_STRING_TYPES))
def assert_status(unique_name, ws_less_9000_rec, tag_type):
    parameters = Constructor.tag_select_payload(ds=ws_less_9000_rec)
    response = TagSelect.get(parameters)

    if tag_type == 'generated true Tag':
        assert unique_name in response.json()["tag-list"]
    elif tag_type == 'generated _note Tag':
        assert '_note' in response.json()["tag-list"]
