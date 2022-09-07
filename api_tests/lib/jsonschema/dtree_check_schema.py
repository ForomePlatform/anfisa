"""
This module contains DtreeCheck schemas
"""

dtree_check_schema = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string"
        },
        "error": {
            "type": "string"
        },
        "line": {
            "type": "integer"
        },
        "pos": {
            "type": "integer"
        }
    },
    "required": [
        "code"
    ]
}
