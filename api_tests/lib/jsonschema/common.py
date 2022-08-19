"""
This module contains common jsonschemas
"""

numeric_stat_list = {
    "type": "object",
    "description": "Positive response of ds2ws endpoint",
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
        "min": {
            "type": [
                "integer",
                "float"
            ]
        },
        "max": {
            "type": [
                "integer",
                "float"
            ]
        },
        "counts": {
            "type": "array",
            "items": {
                "type": "integer"
            },
            "maxItems": 3
        },
        "histogram": {
            "type": "array"
        },
        "required": ["name", "kind", "vgroup", "classes"]
    }
}

enum_stat_list = {
    "type": "object",
    "description": "Positive response of ds2ws endpoint",
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
            "type": "array"
        },
        "required": ["name", "kind", "vgroup", "classes"]
    }
}

func_stat_list = {
    "type": "object",
    "description": "Positive response of ds2ws endpoint",
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
        "variants": ["null", "array"],
        "err": "string",
        "rq-id": "string",
        "no": "string",
        "required": ["name", "kind", "vgroup", "classes", "rq-id"]
    }
}
