"""
This module contains Ds2ws schemas
"""

ds2ws_schema = {
    "type": "object",
    "description": "Positive response of ds2ws endpoint",
    "properties": {
        "task_id": {
            "type": "string"
        }
    },
    "required": [
        "task_id"
    ]
}
