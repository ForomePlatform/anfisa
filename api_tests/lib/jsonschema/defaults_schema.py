"""
This module contains Defaults schemas
"""

defaults_schema = {
    "type": "object",
    "required": ["ws.max.count", "export.max.count", "tab.max.count", "ds.name.max.length", "tag.name.max.length",
                 "sol.name.max.length", "xl.view.count.full", "xl.view.count.samples.default",
                 "xl.view.count.samples.min", "xl.view.count.samples.max", "solution.std.mark", "variety.max.rest.size",
                 "run-options", "run-modes", "job-vault-check-period", "ds-name", "can-drop-ds"],
    "properties": {
        "ws.max.count": {
            "type": "number"
        },
        "export.max.count": {
            "type": "number"
        },
        "tab.max.count": {
            "type": "number"
        },
        "ds.name.max.length": {
            "type": "number"
        },
        "tag.name.max.length": {
            "type": "number"
        },
        "sol.name.max.length": {
            "type": "number"
        },
        "xl.view.count.full": {
            "type": "number"
        },
        "xl.view.count.samples.default": {
            "type": "number"
        },
        "xl.view.count.samples.min": {
            "type": "number"
        },
        "xl.view.count.samples.max": {
            "type": "number"
        },
        "solution.std.mark": {
            "type": "string"
        },
        "variety.max.rest.size": {
            "type": "number"
        },
        "run-options": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "run-modes": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "job-vault-check-period": {
            "type": "number"
        },
        "ds-name": {
            "type": "string"
        },
        "can-drop-ds": {
            "type": "boolean"
        }
    }
}
