from .druid import DruidCfg

DRUID_LOAD_TEMPLATE = {
  "type" : "index",
  "spec" : {
    "dataSchema" : {
      "dataSource" : "?",
      "parser" : {
        "type" : "string",
        "parseSpec" : {
          "format" : "json",
          "dimensionsSpec" : {
            "dimensions" : [
                {"name": "_ord", "type": "long"},
                {"name": "_rand", "type": "long"}],
            "dimensionExclusions" : [],
            "spatialDimensions" : []
          },
          "timestampSpec": {
            "column": "time"
          }
        }
      },
      "metricsSpec" : [],
      "granularitySpec" : {
        "type" : "uniform",
        "segmentGranularity" : DruidCfg.GRANULARITY,
        "queryGranularity" : "none",
        "intervals" : [DruidCfg.INTERVAL],
        "rollup" : False
      }
    },
    "ioConfig" : {
      "type" : "index",
      "firehose" : {
        "type" : "local",
        "baseDir" : "?",
        "filter" : "?"
      },
      "appendToExisting" : False
    },
    "tuningConfig" : {
      "type" : "index",
      "targetPartitionSize" : 5000000,
      "maxRowsInMemory" : 25000,
      "forceExtendableShardSpecs" : True
    }
  }
}
