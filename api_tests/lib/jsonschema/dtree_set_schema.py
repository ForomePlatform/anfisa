"""
This module contains DtreeSet jsonschema
"""

dtree_set_schema = {
    "type": "object",
    "required": [],
    "properties": {
        "kind": {
            "type": "string"
        },
        "total-counts": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "point-counts": {
            "anyOf": [
                {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                {
                    "type": "null"
                }
            ]
        },
        "dtree-list": {
            "type": "array"
        },
        "dtree-sol-version": {
            "type": "number"
        },
        "rq-id": {
            "type": "string"
        },
        "points": {
            "type": "array"
        },
        "cond-atoms": {
            "type": "object"
        },
        "err-atoms": {
            "type": "object"
        },
        "labels": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "code": {
            "type": "string"
        },
        "error": {
            "type": "string"
        },
        "line": {
            "type": "string"
        },
        "pos": {
            "type": "string"
        },
        "hash": {
            "type": "string"
        },
        "dtree-name": {
            "type": "string"
        },
        "eval-status": {
            "type": "string"
        }
    }
}
