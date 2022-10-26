"""
This module contains WsList jsonschema
"""

ws_list_schema = {
    "type": "object",
    "required": [],
    "properties": {
        "ds": {
            "type": "string"
        },
        "total-counts": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "filtered-counts": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "records": {
            "type": "array",
        },
        "active-samples": {
            "type": "string"
        }
    }
}
