"""
This module contains Export jsonschema
"""

export_schema = {
  "type": "object",
  "required": ["kind", "fname"],
  "properties": {
    "kind": {
      "type": "string"
    },
    "fname": {
      "type": "string"
    }
  }
}