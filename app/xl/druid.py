#==================================
class DruidCfg:
    INDEX_URL = "http://localhost:8090/druid/indexer/v1/task"
    QUERY_URL = "http://localhost:8082/druid/v2"
    SQL_URL   = "http://localhost:8082/druid/v2/sql"
    COORD_URL = "http://localhost:8081/druid/coordinator/v1"

    GRANULARITY = "all"
    INTERVAL = "2015-01-01/2015-12-31"
