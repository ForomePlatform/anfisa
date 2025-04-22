"""
This module contains ExportWs jsonschema
"""

export_ws_schema = {
    "type": "object",
    "required": ["kind", "url"],
    "properties": {
        "kind": {
            "type": "string"
        },
        "url": {
            "type": "string"
        }
    }
}
