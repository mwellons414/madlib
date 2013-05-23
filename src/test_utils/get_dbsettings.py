
from madlib.src.template.lib import PSQL1
from madlib.src.test_utils.utils import biprint
from tinctest import logger
import os
import re
import sys

# All values are decided by environment variables
# and default values of psql
db_default = dict()

# ------------------------------------------------------------------------

def get_user_set ():
    """
    Get the user settings
    """
    try:
        import madlib.settings.dbsettings
        if os.environ.has_key("DB_CONFIG"):
            value = os.environ.get("DB_CONFIG")
            try:
                user_set = getattr(madlib.settings.dbsettings, value)
            except:
                biprint("""
                        MADlib Test Error: No such database settings !
       
                        The database setting file is located at
                        settings/dbsettings.py
                        """)
                sys.exit(1)
        else:
            user_set = None
    except:
        logger.info("-- No dbsettings file is provided, use default values! --")
        user_set = None
    return user_set

# ------------------------------------------------------------------------

def get_db_name ():
    """
    Check whether dbname is None in the db_settings
    """
    user_set = get_user_set()
    if user_set is None:
        return None
    else:
        if "dbname" in user_set.keys():
            return user_set["dbname"]
        else:
            return None

# ------------------------------------------------------------------------
            
def get_schema_madlib ():
    """
    Get the schema name for madlib
    """
    user_set = get_user_set()
    if user_set is None:
        return "madlib"
    else:
        if "schema_madlib" in user_set.keys():
            return user_set["schema_madlib"]
        else:
            return "madlib"

# ------------------------------------------------------------------------

def get_schema_testing ():
    """
    Get the schema name for testing
    """
    user_set = get_user_set()
    if user_set is None:
        return "madlibtestdata"
    else:
        if "schema_testing" in user_set.keys():
            return user_set["schema_testing"]
        else:
            return "madlibtestdata"

# ------------------------------------------------------------------------

def get_dbsettings (class_name, dbname = None, force = False):
    """
    Get the database settings from environment
    @param force When it is true, dbname must be used
    """
    # default values
    db = dict(dbname = dbname, # default value for PULSE
              username = None,
              userpwd = None,
              schema_madlib = "madlib",
              schema_testing = "madlibtestdata",
              host = None, 
              port = None,
              pg_options = None,
              psql_options = None,
              superuser = None,
              superpwd = None,
              kind = None,
              master_dir = None,
              version = None)

    user_set = get_user_set()
    if user_set is not None:
        for key in user_set.keys():
            if user_set[key] is not None:
                db[key] = user_set[key]

    if force: db["dbname"] = dbname
    
    if db["master_dir"] is None and class_name != "MADlibTestCase":
        out = PSQL1.run_sql_command(sql_cmd = "show data_directory",
                                    dbname = db["dbname"],
                                    username = db["superuser"],
                                    password = db["superpwd"],
                                    host = db["host"],
                                    port = db["port"],
                                    PGOPTIONS = db["pg_options"],
                                    psql_options = db["psql_options"])
        if out == '':
            sys.exit("****** MADlib test error: cannot execute the query to find master directory! ******")
        m = re.search(r"\s*(/[^\n]*)\n", out)
        db["master_dir"] = m.group(1)

    if db["kind"] is None:
        out = PSQL1.run_sql_command(sql_cmd = "select version()",
                                    dbname = db["dbname"],
                                    username = db["username"],
                                    password = db["userpwd"],
                                    host = db["host"],
                                    port = db["port"],
                                    PGOPTIONS = db["pg_options"],
                                    psql_options = db["psql_options"])
        m = re.search(r"Greenplum", out)
        if m is None:
            db["kind"] = "postgres"
        else:
            db["kind"] = "greenplum"
    else:
        db["kind"] = db["kind"].lower()

    if db["version"] is None:
        out = PSQL1.run_sql_command(sql_cmd = "select version()",
                                    dbname = db["dbname"],
                                    username = db["username"],
                                    password = db["userpwd"],
                                    host = db["host"],
                                    port = db["port"],
                                    PGOPTIONS = db["pg_options"],
                                    psql_options = db["psql_options"])
        if db["kind"] == "postgres":
            m = re.search(r"PostgreSQL (\S+)", out)
        else:
            m = re.search(r"Greenplum Database (\S+)", out)
        db["version"] = m.group(1)            

    # validate the result
    if (not isinstance(db["kind"], str) or
        db["kind"] not in ["postgres", "greenplum"]):
        sys.exit("Database setting error: only 'postgres' and 'greenplum' are supported!")

    # if (not isinstance(db["platform"], str) or
    #     db["platform"].lower() not in ["linux", "mac"]):
    #     sys.exit("Database setting error: only 'linux' and 'mac' are supported!")
    # else:
    #     db["platform"] = db["platform"].lower()
        
    return db
