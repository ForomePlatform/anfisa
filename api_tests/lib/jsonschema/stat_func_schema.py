"""
This module contains stat_func jsonschema
"""

property_status_for_stat_func = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "vgroup": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "sub-kind": {
            "type": "string"
        },
        "render-mode": {
            "type": "string"
        },
        "tooltip": {
            "type": "string"
        },
        "incomplete": {
            "type": "boolean"
        },
        "detailed": {
            "type": "array"
        },
        "variants": {
            "anyOf": [
                {
                    "type": "array"
                },
                {
                    "type": "null"
                }
            ]
        },
        "err": {
            "type": "string"},
        "rq-id": {
            "type": "string"},
        "no": {
            "type": "string"}
    },
    "required": ["name", "kind", "vgroup", "classes", "rq-id"]
}
