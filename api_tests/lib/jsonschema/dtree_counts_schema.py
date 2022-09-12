"""
This module contains DtreeCounts schemas
"""

dtree_counts_schema = {
    "type": "object",
    "required": [
        "point-counts",
        "rq-id"
    ],
    "properties": {
        "point-counts": {
            "anyOf": [
                {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                },
                {
                    "type": "array",
                    "items": {
                        "type": "array"
                    }
                },
                {
                    "type": "array",
                    "items": {
                        "type": "null"
                    }
                }
            ]
        }
    },
    "rq-id": {
        "type": "string"
    }
}
