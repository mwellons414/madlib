
import madlib.settings.dbsettings
import os
import sys

# All values are decided by environment variables
# and default values of psql
db_default = dict()

# ----------------------------------------------------------------

def get_dbsettings (class_name):
    """
    Get the database settings from environment
    """
    # default values
    db = dict(dbname = None,
              username = None,
              userpwd = None,
              schema_madlib = "madlib",
              schema_testing = "madlibtestdata",
              host = None, 
              port = None,
              pg_options = None,
              psql_options = None,
              platform = "linux",
              superuser = None,
              superpwd = None,
              kind = "greenplum",
              master_dir = None,
              env = None)
    
    if os.environ.has_key("DB_CONFIG"):
        value = os.environ.get("DB_CONFIG")
        try:
            user_set = getattr(madlib.settings.dbsettings, value)
        except:
            print("""
                  MADlib Test Error: No such database settings for """
                  + class_name + """!

                  The database setting file is located at
                  settings/dbsettings.py
                  """)
            sys.exit(1)
    else:
        user_set = db_default # madlib.settings.dbsettings.default
        
    for key in user_set.keys():
        db[key] = user_set[key]

    # validate the result
    if (not isinstance(db["kind"], str) or
        db["kind"].lower() not in ["postgres", "greenplum"]):
        sys.exit("Database setting error: only 'postgres' and 'greenplum' are supported!")
    else:
        db["kind"] = db["kind"].lower()

    if (not isinstance(db["platform"], str) or
        db["platform"].lower() not in ["linux", "mac"]):
        sys.exit("Database setting error: only 'linux' and 'mac' are supported!")
    else:
        db["platform"] = db["platform"].lower()
        
    return db
