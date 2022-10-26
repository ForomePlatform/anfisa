"""
This module contains DirInfo schemas
"""

dir_info_schema = {
    "type": "object",
    "required": ["version", "build-hash", "ds-list"],
    "properties": {
        "version": {
            "type": "string"
        },
        "build-hash": {
            "type": "string"
        },
        "ds-list": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "ds-dict": {
                "type": "object"
            },
        "documentation": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "url"],
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "url": {
                        "type": "string"
                    }
                }
            }
        }
    }
}
