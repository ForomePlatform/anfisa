"""
This module Dsinfo jsonschema
"""

dsinfo_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "upd-time": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "create-time": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "note": {
            "type": "string"
        },
        "doc": {
            "type": "array"
        },
        "total": {
            "type": "integer"
        },
        "date-note": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "ancestors": {
            "type": "array"
        },
        "meta": {
            "type": "object"
        },
        "cohorts": {
            "type": "array"
        },
        "unit-classes": {
            "type": "array"
        },
        "export-max-count": {
            "type": "integer"
        },
        "unit-groups": {
            "type": "array"
        }
    },
    "required": [
        "name",
        "kind",
        "create-time",
        "upd-time",
        "note",
        "date-note",
        "total",
        "doc",
        "ancestors",
        "meta",
        "unit-classes",
        "unit-groups"
    ]
}
