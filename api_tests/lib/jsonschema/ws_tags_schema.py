"""
This module contains WsTags jsonschema
"""

ws_tags_schema = {
    "type": "object",
    "properties": {
        "check-tags": {
            "type": "array",
        },
        "op-tags": {
            "type": "array"
        },
        "rec-tags": {
            "type": "object"
        },
        "upd-time": {
            "type": ["string", "null"]
        },
        "upd-from": {
            "type": ["string", "null"]
        },
        "filters": {
            "type": "array",
        },
        "tags-state": {
            "type": "integer"
        }
    },
    "required": [
        "check-tags",
        "op-tags",
        "rec-tags",
        "filters",
        "tags-state"
    ]
}
