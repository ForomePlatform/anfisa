"""
This module contains TagSelect jsonschema
"""

tag_select_schema = {
  "type": "object",
  "required": ["tag-list", "tags-rec-list"],
  "properties": {
    "tag-list": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "tag": {
       "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ]
    },
    "tags-state": {
      "type": "number"
    },
    "tags-rec-list": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}