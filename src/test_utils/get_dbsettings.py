
import madlib.settings.dbsettings
import os
import sys

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
              psql_options = None) 
    
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
        user_set = madlib.settings.dbsettings.default
    for key in user_set.keys():
        db[key] = user_set[key]
    return db
