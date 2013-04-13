
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
             user_testing = "gpdbchina",
             user_root = "gpdbchina",
             host = "localhost",
             port = 55000,
             schema_madlib = "madlib",
             schema_testing = "madlibtestdata")

# ------------------------------------------------------------------------

# maddemo machine setting
demo = dict(dbname = "madlib",
            user_testing = "gpdbchina",
            user_root = "gpdbchina",
            pwd_testing = None,
            host = "maddemo.greenplum.com", 
            port = 55000,
            schema_madlib = "madlib",
            schema_testing = "madlibtestdata")



