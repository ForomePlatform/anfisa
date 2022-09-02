"""
This module contains DtreeStat jsonschema
"""

dtree_stat_schema = {
    "type": "object",
    "properties": {
        "total-counts": {
            "type": "array",
            "items": {
                "type": "integer"
            },
            "minItems": 1,
            "maxItems": 3
        },
        "filtered-counts": {
            "type": "array",
            "items": {
                "type": "integer"
            },
            "minItems": 1,
            "maxItems": 3
        },
        "stat-list": {
            "type": "array",
            "items": {
                "type": "object",
            }
        },
        "functions": {
            "type": "array",
            "items": {
                "type": "object"
            }
        },
        "rq-id": {
            "type": "string"
        }
    },
    "required": ["total-counts", "filtered-counts", "stat-list", "functions", "rq-id"]
}
