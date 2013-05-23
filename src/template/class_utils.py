
from madlib.src.test_utils.utils import biprint
from madlib.src.template.skip_table import version_skip_map
import os
import re
import sys

def make_sure_path_exists (cls, path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            sys.exit("""
                     MADlib Test Error: cannot create """ + path + """
                     with """ + cls.__module__ + "." + cls.__name__ + " !")

# -----------------------------------------------------------------

def get_env_flag (cls, flag, origin = False):
    """
    Get the environment variable for
    creating case or answer file
    """
    if os.environ.has_key(flag):
        value = os.environ.get(flag).lower()
        if (value == "t" or value == "true" or
            value == "yes" or value == "y"):
            return True
        elif (value == "f" or value == "false" or
              value == "n" or value == "no"):
            return False
    return origin

# -----------------------------------------------------------------

def get_ext_ans (cls, flag):
    """
    Get the environment variable for
    creating answer file using
    external script, which takes in
    parameters and compute the results
    """
    if os.environ.has_key(flag):
        if not cls.create_ans_:
            biprint("""
                  MADlib Test Error: """ + cls.__module__ + "." + cls.__name__ +
                  """
                  R_ANS list only plays an role when CREATE_ANS=T.

                  When CREATE_ANS=T and R_ANS=R_script_path, the R
                  script will be executed using the parameters passed
                  from test executor to create results.
                  """)
            sys.exit(1)
            
        value = os.environ.get(flag)
        return (True, value)
    return (False, None)

# ----------------------------------------------------------------

def get_skip (cls):
    """
    Get skip list
    """
    do_skip_err = False
    if os.environ.has_key("SKIP"):
        value = os.environ.get("SKIP")
        if value != "":
            m = re.match(r"^(.+)\.([^\.]+)$", value)
            if m is None: # value is just a dict name
                if cls.skip_file is None:
                    return []
                if os.path.exists("./" + cls.skip_file): # check current path
                    ms = os.path.splitext(cls.skip_file)[0]
                    sys.path.append(os.getcwd())
                else:
                    s = os.path.basename(cls.skip_file)
                    s = os.path.splitext(s)[0]
                    mm = re.match(r"^(.+)\.([^\.]+)$", cls.__module__)
                    if mm is None:
                        ms = s
                    else:
                        ms = mm.group(1) + "." + s
                try:
                    md = __import__(ms, fromlist = '1')
                    user_skip = getattr(md, value)
                except:
                    do_skip_err = True
            else:
                try:
                    md = __import__(m.group(1), fromlist = '1')
                    user_skip = getattr(md, m.group(2))
                    # skip_list_name = value
                except:
                    do_skip_err = True
        else:
            user_skip = []
    else:
        user_skip = []

    if len(user_skip) > 0:
        biprint("-- skip-list '" + value + "' is used.")

    if cls.skip_file is None:
        version_skip = []
    else:
        if os.path.exists("./" + cls.skip_file): # check current path
            ms = os.path.splitext(cls.skip_file)[0]
            sys.path.append(os.getcwd())
        else:
            s = os.path.basename(cls.skip_file)
            s = os.path.splitext(s)[0]
            mm = re.match(r"^(.+)\.([^\.]+)$", cls.__module__)
            if mm is None:
                # ms = cls.__module__ + "." + s
                ms = s
            else:
                ms = mm.group(1) + "." + s
        md = __import__(ms, fromlist = '1')
        version_skip = version_skip_map(cls.db_settings_["kind"],
                                        cls.db_settings_["version"],
                                        md)

    if do_skip_err: # something went wrong
        biprint("""
              MADlib Test Error: No skip definitions for 
              """
              + cls.__module__ + "." + cls.__name__ + """ !
              
              Either you explicitly define the class variable skip_file in
              you test case class, or you put the skip list into the default
              skip file skip.py.

              The environment variable SKIP can have value like:
              SKIP=examples.linregr_skip.skip_all, which will override
              the skip_file,
              or
              just SKIP=skip_all, and we will search for the skip list in
              skip_file
              """)
        sys.exit(1)

    if (len(cls.skip)):
        biprint("-- skip-list '" + cls.skip + "' is used.")
        
    return user_skip + cls.skip + version_skip
