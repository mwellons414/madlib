# ------------------------------------------------------------------------
# Setting database properties
#
# Setting value to None uses the default values of psql
# When port is None, it uses the environment variable $PGPORT
# ------------------------------------------------------------------------

# Personal laptop settings
# All values are decided by environment variables
# and default values of psql
default = dict()

# ------------------------------------------------------------------------

# default PULSE setting
pulse = dict(dbname = "madlib",
             username = "gpdbchina",
             superuser = "gpdbchina",
             host = "localhost",
             port = 55000,
             schema_madlib = "madlib",
             schema_testing = "madlibtestdata")

# ------------------------------------------------------------------------

# maddemo machine setting
# As an example, this has all the parameters
demo = dict(dbname = "madlib",
            username = "gpdbchina", # tesing user
            userpwd = None,
            host = "maddemo.greenplum.com", 
            port = 55000,
            schema_madlib = "madlib",
            schema_testing = "madlibtestdata",
            pg_options = None, # PG server options
            psql_options = "-x", # PG client options, expended view of result, might be easier to process
            # ------------------------------------------------
            # The following are only for data loader
            # Future data loader may have different settings
            superuser = "gpdbchina",
            superpwd = None,
            kind = "greenplum", 
            master_dir = "maybe useful",
            env = "~/.local/bin/gp-remote")

# ------------------------------------------------------------------------

# Postgres on demo machine
demopg = dict(dbname = "gpdbchina",
              username = "gpdbchina",
              userpwd = None,
              host = "localhost",
              port = 5455,
              schema_madlib = "madlib",
              schema_testing = "madlibtestdata",
              psql_options = "-x",
              superuser = "gpdbchina",
              superpwd = None,
              kind = "postgres",
              master_dir = "/data/hai/pg_data",
              env = "/data/hai/local/bin/pg")

# ------------------------------------------------------------------------

# Hai's GPDB
haigp = dict(dbname = "qianh1",
             username = "madlibtester", # tesing user
             userpwd = None,
             host = "localhost", 
             port = 14526,
             schema_madlib = "madlib",
             schema_testing = "madlibtestdata",
             # ------------------------------------------------
             # The following are only for data loader
             # Future data loader may have different settings
             superuser = "qianh1",
             superpwd = None,
             kind = "greenplum", 
             master_dir = "/Users/qianh1/.gp/greenplum-db-4.2.5.0-data/master/gpseg-1",
             env = "/Users/qianh1/.local/bin/gp")

# ------------------------------------------------------------------------

# Hai's Postgres
haipg = dict(dbname = "qianh1",
             username = "qianh1", # tesing user
             userpwd = None,
             host = "localhost", 
             port = 5433,
             schema_madlib = "madlib",
             schema_testing = "madlibtestdata",
             # ------------------------------------------------
             # The following are only for data loader
             # Future data loader may have different settings
             superuser = "qianh1",
             superpwd = None,
             kind = "postgres", 
             master_dir = "/Users/qianh1/.pg/pg92_data",
             env = "/Users/qianh1/.local/bin/pg")




