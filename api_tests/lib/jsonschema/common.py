"""
This module contains common jsonschemas
"""

numeric_property_status_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "vgroup": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "sub-kind": {
            "type": "string"
        },
        "render-mode": {
            "type": "string"
        },
        "tooltip": {
            "type": "string"
        },
        "incomplete": {
            "type": "boolean"
        },
        "detailed": {
            "type": "array"
        },
        "min": {
            "type": "number"
        },
        "max": {
            "type": "number"
        },
        "counts": {
            "type": "array",
            "items": {
                "type": "integer"
            },
            "maxItems": 3
        },
        "histogram": {
            "type": "array"
        }
    },
    "required": ["name", "kind", "vgroup", "classes"]
}

enum_property_status_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "vgroup": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "sub-kind": {
            "type": "string"
        },
        "render-mode": {
            "type": "string"
        },
        "tooltip": {
            "type": "string"
        },
        "incomplete": {
            "type": "boolean"
        },
        "detailed": {
            "type": "array"
        },
        "variants": {
            "type": "array"
        }
    },
    "required": ["name", "kind", "vgroup", "classes"]
}

func_property_status_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "kind": {
            "type": "string"
        },
        "vgroup": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "sub-kind": {
            "type": "string"
        },
        "render-mode": {
            "type": "string"
        },
        "tooltip": {
            "type": "string"
        },
        "incomplete": {
            "type": "boolean"
        },
        "detailed": {
            "type": "array"
        },
        "variants": {
            "anyOf": [
                {
                    "type": "array"
                },
                {
                    "type": "null"
                }
            ]
        },
        "err": {
            "type": "string"},
        "no": {
            "type": "string"}
    },
    "required": ["name", "kind", "vgroup", "classes"]
}

solution_entry_schema = {
  "type": "object",
  "required": ["name", "standard", "eval-status"],
  "properties": {
    "name": {
      "type": "string"
    },
    "standard": {
      "type": "boolean"
    },
    "upd-time": {
      "type": "string"
    },
    "upd-from": {
      "type": "string"
    },
    "rubric": {
      "type": "string"
    },
    "eval-status": {
      "type": "string"
    }
  }
}