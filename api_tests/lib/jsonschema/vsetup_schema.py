"""
This module contains Vsetup jsonschema
"""

vsetup_schema = {
    "type": "object",
    "required": [],
    "properties": {
        "aspects": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "name",
                    "title",
                    "source",
                    "ignored",
                    "attrs"
                ],
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "source": {
                        "type": "string"
                    },
                    "ignored": {
                        "type": "boolean"
                    },
                    "mode": {
                        "type": "string"
                    },
                    "attrs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "name",
                                "kind",
                                "title",
                                "is_seq"
                            ],
                            "properties": {
                                "name": {
                                    "anyOf": [
                                        {
                                            "type": "string"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ]
                                },
                                "kind": {
                                    "type": "string"
                                },
                                "title": {
                                    "anyOf": [
                                        {
                                            "type": "string"
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ]
                                },
                                "is_seq": {
                                    "type": "boolean"
                                },
                                "tooltip": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "field": {
                        "type": "string"
                    }
                }
            }
        }
    }
}
