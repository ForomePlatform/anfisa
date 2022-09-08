"""
This module contains Zone_list jsonschema
"""

zone_descriptor_serial = {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["title", "zone"],
    "properties": {
      "zone": {
        "type": "string"
      },
      "title": {
        "type": "string"
      }
    }
  }
}

zone_descriptor_single = {
  "type": "object",
  "required": ["zone", "title", "variants"],
  "properties": {
    "zone": {
      "type": "string"
    },
    "title": {
      "type": "string"
    },
    "variants": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}