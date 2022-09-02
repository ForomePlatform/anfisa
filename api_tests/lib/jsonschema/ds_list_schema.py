"""
This module contains DsList jsonschema
"""

ds_list_schema = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string"
        }
    },
    "required": [
        "task_id"
    ]
}
