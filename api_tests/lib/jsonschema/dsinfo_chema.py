"""
This module Dsinfo jsonschema
"""

dsinfo_schema = {
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "upd-time": {
      "type": "string"
    },
    "create-time": {
      "type": "string"
    },
    "kind": {
      "type": "string"
    },
    "note": {
      "type": "string"
    },
    "doc": {
      "type": "array",
      "items": [
        {
          "type": "null"
        },
        {
          "type": "array",
          "items": [
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "array",
                  "items": [
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        }
                      ]
                    },
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "array",
                  "items": [
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        },
                        {
                          "type": "object",
                          "properties": {
                            "image": {
                              "type": "string"
                            },
                            "type": {
                              "type": "string"
                            }
                          },
                          "required": [
                            "image",
                            "type"
                          ]
                        }
                      ]
                    },
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        }
                      ]
                    },
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        },
                        {
                          "type": "object",
                          "properties": {
                            "images": {
                              "type": "array",
                              "items": [
                                {
                                  "type": "string"
                                },
                                {
                                  "type": "string"
                                },
                                {
                                  "type": "string"
                                }
                              ]
                            },
                            "names": {
                              "type": "array",
                              "items": [
                                {
                                  "type": "string"
                                },
                                {
                                  "type": "string"
                                },
                                {
                                  "type": "string"
                                }
                              ]
                            },
                            "type": {
                              "type": "string"
                            }
                          },
                          "required": [
                            "images",
                            "names",
                            "type"
                          ]
                        }
                      ]
                    },
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        },
                        {
                          "type": "object",
                          "properties": {
                            "image": {
                              "type": "string"
                            },
                            "type": {
                              "type": "string"
                            }
                          },
                          "required": [
                            "image",
                            "type"
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "array",
                  "items": [
                    {
                      "type": "array",
                      "items": [
                        {
                          "type": "string"
                        },
                        {
                          "type": "string"
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    "total": {
      "type": "integer"
    },
    "date-note": {
      "type": "null"
    },
    "ancestors": {
      "type": "array",
      "items": {}
    },
    "meta": {
      "type": "object",
      "properties": {
        "case": {
          "type": "string"
        },
        "cohorts": {
          "type": "array",
          "items": {}
        },
        "data_schema": {
          "type": "string"
        },
        "modes": {
          "type": "array",
          "items": [
            {
              "type": "string"
            }
          ]
        },
        "proband": {
          "type": "string"
        },
        "record_type": {
          "type": "string"
        },
        "samples": {
          "type": "object",
          "properties": {
            "NA24143": {
              "type": "object",
              "properties": {
                "affected": {
                  "type": "boolean"
                },
                "family": {
                  "type": "string"
                },
                "father": {
                  "type": "string"
                },
                "id": {
                  "type": "string"
                },
                "mother": {
                  "type": "string"
                },
                "name": {
                  "type": "string"
                },
                "sex": {
                  "type": "integer"
                }
              },
              "required": [
                "affected",
                "family",
                "father",
                "id",
                "mother",
                "name",
                "sex"
              ]
            },
            "NA24149": {
              "type": "object",
              "properties": {
                "affected": {
                  "type": "boolean"
                },
                "family": {
                  "type": "string"
                },
                "father": {
                  "type": "string"
                },
                "id": {
                  "type": "string"
                },
                "mother": {
                  "type": "string"
                },
                "name": {
                  "type": "string"
                },
                "sex": {
                  "type": "integer"
                }
              },
              "required": [
                "affected",
                "family",
                "father",
                "id",
                "mother",
                "name",
                "sex"
              ]
            },
            "NA24385": {
              "type": "object",
              "properties": {
                "affected": {
                  "type": "boolean"
                },
                "family": {
                  "type": "string"
                },
                "father": {
                  "type": "string"
                },
                "id": {
                  "type": "string"
                },
                "mother": {
                  "type": "string"
                },
                "name": {
                  "type": "string"
                },
                "sex": {
                  "type": "integer"
                }
              },
              "required": [
                "affected",
                "family",
                "father",
                "id",
                "mother",
                "name",
                "sex"
              ]
            }
          },
          "required": [
            "NA24143",
            "NA24149",
            "NA24385"
          ]
        },
        "versions": {
          "type": "object",
          "properties": {
            "Anfisa load": {
              "type": "string"
            },
            "GERP": {
              "type": "string"
            },
            "annotations": {
              "type": "string"
            },
            "annotations_build": {
              "type": "string"
            },
            "annotations_date": {
              "type": "string"
            },
            "bcftools_annotate_version": {
              "type": "string"
            },
            "gatk": {
              "type": "string"
            },
            "gatk_select_variants": {
              "type": "string"
            },
            "pipeline": {
              "type": "string"
            },
            "reference": {
              "type": "string"
            },
            "vep_version": {
              "type": "string"
            }
          },
          "required": [
            "Anfisa load",
            "GERP",
            "annotations",
            "annotations_build",
            "annotations_date",
            "bcftools_annotate_version",
            "gatk",
            "gatk_select_variants",
            "pipeline",
            "reference",
            "vep_version"
          ]
        }
      },
      "required": [
        "case",
        "cohorts",
        "data_schema",
        "modes",
        "proband",
        "record_type",
        "samples",
        "versions"
      ]
    },
    "cohorts": {
      "type": "array",
      "items": {}
    },
    "unit-classes": {
      "type": "array",
      "items": [
        {
          "type": "object",
          "properties": {
            "title": {
              "type": "string"
            },
            "values": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          },
          "required": [
            "title",
            "values"
          ]
        },
        {
          "type": "object",
          "properties": {
            "title": {
              "type": "string"
            },
            "values": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          },
          "required": [
            "title",
            "values"
          ]
        },
        {
          "type": "object",
          "properties": {
            "title": {
              "type": "string"
            },
            "values": {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          },
          "required": [
            "title",
            "values"
          ]
        }
      ]
    },
    "export-max-count": {
      "type": "integer"
    },
    "unit-groups": {
      "type": "array",
      "items": [
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                },
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                }
              ]
            }
          ]
        },
        {
          "type": "array",
          "items": [
            {
              "type": "string"
            },
            {
              "type": "array",
              "items": [
                {
                  "type": "string"
                }
              ]
            }
          ]
        }
      ]
    },
    "igv-urls": {
      "type": "array",
      "items": [
        {
          "type": "string"
        },
        {
          "type": "string"
        },
        {
          "type": "string"
        }
      ]
    }
  },
  "required": [
    "name",
    "upd-time",
    "create-time",
    "kind",
    "note",
    "doc",
    "total",
    "date-note",
    "ancestors",
    "meta",
    "cohorts",
    "unit-classes",
    "export-max-count",
    "unit-groups",
    "igv-urls"
  ]
}
