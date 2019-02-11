from app.congig import Cfg
#===============================================
class MySQL_Supp:
    VAULT_CREATE = (
        "CREATE TABLE __VAULT__` ("
        "  `name` varchar(32) NOT NULL,"
        "  `kind` enum('ws','xl') NOT NULL,"
        "  `active` bool NOT NULL,"
        "  `base_ds` varchar(32),"
        "  `view_schema` mediumtext NOT NULL,"
        "  `flt_schema` mediumtext NOT NULL,"
        "  `view_stat` mediumtext NOT NULL,"
        "  PRIMARY KEY (`name`)"
        ") ENGINE=InnoDB")

    VAULT_INSERT = (
        "INSERT INTO __VAULT__ ("
        "name, kind, active, base_ds, view_schema, flt_schema, view_stat)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s)")

    VAULT_UPDATE_ACTIVE = (
        "UPDATE __VAULT__ set active = %s WHERE name = %s")

    VAULT_INFO = (
            "SELECT name, kind, active, base_ds, view_schema, flt_schema ",
            "FROM __VAULT__ WHERE name = %s")

    #==========================
    def VIEW_CREATE(ds_name):
        return (
            "CREATE TABLE VIEW_%s` ("
            "  `rec_no` int(11) NOT NULL,"
            "  `label` varchar(50) NOT NULL,"
            "  `color` varchar(10) NOT NULL,"
            "  `uniq` varchar(50) NOT NULL,"
            "  `data` mediumtext NOT NULL,"
            "  PRIMARY KEY (`rec_no`)"
            ") ENGINE=InnoDB") % ds_name

    def VIEW_INSERT(ds_name):
        return (
            ("INSERT INTO VIEW_%s " % ds_name),
            "(rec_no, label, color, uniq, data)  VALUES (%s, %s, %s, %s, %s)")

    #==========================
    def FILTER_CREATE(ds_name):
        return (
            "CREATE TABLE FLT_%s` ("
            "  `rec_no` int(11) NOT NULL,"
            "  `data` mediumtext NOT NULL,"
            "  PRIMARY KEY (`rec_no`)"
            ") ENGINE=InnoDB") % ds_name

    def FILTER_INSERT(ds_name):
        return (
            ("INSERT INTO FLT_%s " % ds_name),
            "(rec_no, data) VALUES (%s, %s)")

#===============================================
class Druid_Supp:
    LOAD_TEMPLATE = {
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
            "segmentGranularity" : Cfg.DRUID_GRANULARITY,
            "queryGranularity" : "none",
            "intervals" : [Cfg.DRUID_INTERVAL],
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


