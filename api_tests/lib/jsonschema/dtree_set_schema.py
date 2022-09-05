"""
This module contains DtreeSet jsonschema
"""

dtree_set_schema = {
    "type": "object",
    "required": [
        "kind",
        "total-counts",
        "point-counts",
        "code",
        "points",
        "cond-atoms",
        "labels",
        "eval-status",
        "hash",
        "dtree-list",
        "dtree-sol-version",
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
                    "type": "array",
                    "items": {
                        "type": "null"
                    }
                },
            ]
        },
        "code": {
            "type": "string"
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

dtree_point_descriptor = {
    "type": "object",
    "required": ["kind", "level", "decision", "code-frag", "actions"],
    "properties": {
        "kind": {
            "type": "string"
        },
        "level": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "decision": {
            "anyOf": [
                {
                    "type": "boolean"
                },
                {
                    "type": "null"
                }
            ]
        },
        "code-frag": {
            "type": "string"
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}

condition_descriptor_numeric = {
    "type": "array",
    "items": {
        "anyOf": [
            {
                "type": "array"
            },
            {
                "type": "string"
            }
        ],
        "items": {
            "anyOf": [
                {
                    "type": "boolean"
                },
                {
                    "type": "number"
                }
            ]
        }
    }
}

condition_discriptor_enum = {
    "type": "array",
    "items": {
        "anyOf": [
            {
                "type": "string"
            },
            {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        ]
    }
}

condition_discriptor_func = {
    "type": "array",
    "items": {
        "anyOf": [
            {
                "type": "string"
            },
            {
                "type": "object"
            },
            {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        ]
    }
}
