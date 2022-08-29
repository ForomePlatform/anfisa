"""
This module contains DsStat jsonschema
"""

ds_stat_schema = {
    "type": "object",
    "required": [
        "kind",
        "total-counts",
        "filtered-counts",
        "stat-list",
        "functions",
        "conditions",
        "cond-seq",
        "eval-status",
        "hash",
        "filter-list",
        "filter-sol-version",
        "rq-id"
    ],
    "properties": {
        "kind": {
            "type": "string"
        },
        "total-counts": {
            "type": "array",
            "items": {
                "type": "number"
            },
            "minItems": 1,
            "maxItems": 1,
        },
        "filtered-counts": {
            "type": "array",
            "items": {
                "type": "number"
            },
            "minItems": 1,
            "maxItems": 1,
        },
        "stat-list": {
            "type": "array"
        },
        "functions": {
            "type": "array"
        },
        "filter-list": {
            "type": "array"
        },
        "cur-filter": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
        },
        "filter-sol-version": {
            "type": "number"
        },
        "rq-id": {
            "type": "string"
        },
        "conditions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "cond-seq": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "eval-status": {
            "type": "string"
        },
        "hash": {
            "type": "string"
        }
    }
}
