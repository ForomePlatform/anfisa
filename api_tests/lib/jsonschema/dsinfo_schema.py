"""
This module Dsinfo schemas
"""

dsinfo_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "create-time": {
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
        "note": {
            "type": "string"
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
        "total": {
            "type": "integer"
        },
        "doc": {
            "type": "array"
        },
        "ancestors": {
            "type": "array"
        },
        "meta": {
            "type": "object"
        },
        "unit-classes": {
            "type": "array"
        },
        "unit-groups": {
            "type": "array",
            "items": {
                "type": ["string", "array"]
            },
        },
        "igv-urls": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "cohorts": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "export-max-count": {
            "type": "integer"
        },
        "receipts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties":
                    {
                        "kind": {
                            "type": "string"
                        },
                        "eval-update-info": {
                            "type": "array"
                        },
                        "panels-supply": {
                            "type": "array"
                        },
                        "f-presentation": {
                            "type": "array"
                        },
                        "filter-name": {
                            "type": "string"
                        },
                        "p-presentation": {
                            "type": "array"
                        },
                        "dtree-name": {
                            "type": "string"
                        }
                    }
            }
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
