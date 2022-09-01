"""
This module contains StatUnits jsonschema
"""

stat_units_schema = {
    "type": "object",
    "required": ["rq-id", "units"],
    "properties": {
        "rq-id": {
            "type": "string"
        },
        "units": {
            "type": "array",
        }
    }
}
