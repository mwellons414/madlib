'''
MADlibTemplateTestCase is a subclass of GPDBTestCase that provides basic 
cababilities to run a templated SQL statement with substitution rules.

For any list parameters passed as "template_vars" it will iterate through 
all combinations
of parameters and generate a separate test case for each combination.
'''

from src.template.sql import MADlibSQLTestCase
from src.template.lib import PSQL1
from src.test_utils.get_dbsettings import get_dbsettings
from src.test_utils.utils import call_R_script
from tinctest import TINCTestLoader
from tinctest.lib import Gpdiff
import new
import os
import re
import sys
import shutil

# ------------------------------------------------------------------------
# Use environment variables to control the behavior:
#
# CREATE_CASE   to create case files
# CREATE_ANS    to create answer files (mainly for input test cases)
# DB_CONFIG     to pick a database configuration from settings.dbsettings
# ------------------------------------------------------------------------

class MADlibTestCase (MADlibSQLTestCase):
    """
    Abstract class for running templated SQL, subclasses must define the template
    """
    # The following variables should be provided by subclass
    schema_madlib   = "madlib"
    schema_testing  = "madlibtestdata"
    sql_dir         = "sql" # store the sql command executed
    out_dir         = "result" # output folder
    ans_dir         = "expected" # expected results
    template        = None  
    template_method = None # method name, controls the file name 
    template_doc    = ""    
    template_vars   = {}
    skip_file = "skip.py"
    skip = []
    create_ans_ = False
    create_case_ = False
    db_settings_ = dict(dbname = None, username = None, userpwd = None,
                        schema_madlib = "madlib",
                        schema_testing = "madlibtestdata",
                        host = None, port = None,
                        pg_options = None, psql_options = None) 
    reserved_keywords_ = ["incr_", "schema_madlib", "schema_testing"]

    # If you want to use fiel names like "linregr_input_test_{incr}",
    # increse incr for every test, which is done in the super class
    # This number is used for file name
    # to avoid putting very long arguments in the file name
    incr_ = 0 # name is hard-coded

    # -----------------------------------------------------------------

    @classmethod
    def _make_sure_path_exists (cls, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                sys.exit("""
                         MADlib Test Error: cannot create """ + path + """
                         with """ + cls.__module__ + "." + cls.__name__ + " !")

    # -----------------------------------------------------------------

    @classmethod
    def _get_env_flag (cls, flag):
        """
        Get the environment variable for
        creating case or answer file
        """
        if os.environ.has_key(flag):
            value = os.environ.get(flag).lower()
            if (value == "t" or value == "true" or
                value == "yes" or value == "y"):
                return True
        return False

    # -----------------------------------------------------------------

    @classmethod
    def _get_ext_ans (cls, flag):
        """
        Get the environment variable for
        creating answer file using
        external script, which takes in
        parameters and compute the results
        """
        if os.environ.has_key(flag):
            if not cls.create_ans_:
                print("""
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

    @classmethod
    def _validate_vars (cls):
        """
        To ensure that the usre provided template_vars
        does not contain the keywords
        """
        anyMatch = any(key in cls.reserved_keywords_ \
                for key in cls.template_vars.keys())
        if anyMatch:
            print("MADlib Test Error: template_vars should not use any of the following keywords:")
            print(cls.reserved_keywords_)
            sys.exit("Testcase is stopping for " + cls.__module__ + "." + cls.__name__ + " !")
        return None

    # ----------------------------------------------------------------

    @classmethod
    def _get_skip (cls):
        """
        Get skip list
        """            
        do_skip_err = False
        skip_list_name = None
        if os.environ.has_key("SKIP"):
            if cls.create_case_ is False:
                print("""
                      MADlib Test Error: """ + cls.__module__ + "." + cls.__name__ + 
                      """SKIP list only plays an role when CREATE_CASE=T.
    
                      The skip-tag will be added to the head of each test case
                      file when it is created. During execution, all files with
                      skip-tag at the beginning of it will be skipped.
                      """)
                sys.exit(1)

            value = os.environ.get("SKIP")
            m = re.match(r"^(.+)\.([^\.]+)$", value)
            if m is None: # value is just a dict name
                if os.path.exists("./" + cls.skip_file): # check current path
                    ms = os.path.splitext(cls.skip_file)[0]
                else:
                    s = os.path.basename(cls.skip_file)
                    s = os.path.splitext(s)[0]
                    mm = re.match(r"^(.+)\.([^\.]+)$", cls.__module__)
                    if mm is None:
                        ms = cls.__module__ + "." + s
                    else:
                        ms = mm.group(1) + "." + s
                try:
                    md = __import__(ms, fromlist = '1')
                    user_skip = getattr(md, value)
                    skip_list_name = ms + "." + value
                except:
                    do_skip_err = True
            else:
                try:
                    md = __import__(m.group(1), fromlist = '1')
                    user_skip = getattr(md, m.group(2))
                    skip_list_name = value
                except:
                    do_skip_err = True
        else:
            user_skip = []

        if do_skip_err: # something went wrong
            print("""
                  MADlib Test Error: No such skip definitions for 
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
        return (user_skip, skip_list_name)
 
    # ----------------------------------------------------------------

    @classmethod
    def _write_params (cls, f, args):
        """
        Write test parameters into the test case file
        """
        for key in args.keys():
            if (key not in cls.reserved_keywords_ and
                isinstance(args[key], str)):
                f.write("-- @madlib-param " + key + " = \""
                        + args[key] + "\"\n")
        return None

    # ----------------------------------------------------------------
    
    @classmethod
    def loadTestsFromTestCase (cls):
        """
        @param cls The child class 
        """
        # Ensure we pickup the variables from our child class
        template        = cls.template
        template_method = cls.template_method
        template_doc    = cls.template_doc
        template_vars   = cls.template_vars

        if template_method is None or template is None:
            print("MADlib Test Error: " + cls.__module__ + "." + cls.__name__ + " !")
            sys.exit("You must define template and template_method!")
       
        cls.create_case_ = cls._get_env_flag("CREATE_CASE")
        cls.create_ans_ = cls._get_env_flag("CREATE_ANS")
        (r_ans, r_script) = cls._get_ext_ans("R_ANS")
        
        # validate cls template_vars
        cls._validate_vars()
        
        cls.db_settings_ = get_dbsettings()
        template_vars.update(schema_madlib = cls.db_settings_["schema_madlib"],
                             schema_testing = cls.db_settings_["schema_testing"])
        skip_file = cls.skip_file
        (skip, skip_name) = cls._get_skip()
            
        # XXX: I'm not completely clear why this is necessary, somehow the loadTests ends up
        # being called twice, once for the child class and once from here.  When called from
        # here we need to not die...
        if template is None:
            return []

        assert isinstance(template,str)
        assert isinstance(template_method,str)

        print "loading tests from test case"

        source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))
        sql_dir = os.path.join(source_dir, cls.sql_dir)
        ans_dir = os.path.join(source_dir, cls.ans_dir)
        out_dir = os.path.join(source_dir, cls.out_dir)

        cls._make_sure_path_exists(sql_dir)
        cls._make_sure_path_exists(ans_dir)
        cls._make_sure_path_exists(out_dir)
 
        # ------------------------------------------------
        # Also create our "Template" test cases
        def makeTest (x):
            cls.incr_ += 1
            x["incr_"] = cls.incr_
            methodName = TINCTestLoader.testMethodPrefix + template_method.format(**x)
            methodDoc  = template_doc.format(**x)
            methodQuery = template.format(**x)

            ## Skip a test case
            add_flag = True
            for case in skip:
                eq = True
                for key in case.keys():
                    if x[key].lower() != case[key].lower():
                        eq = False
                        break
                if eq:
                    add_flag = False
                    break

            if cls.create_case_:
                # Create the SQL test case file that we are going to run
                sql_inputfile = os.path.join(sql_dir, methodName + ".sql")
                with open(sql_inputfile, 'w') as f:
                    if cls.template_doc == "" or cls.template_doc is None:
                        f.write("-- @description " + cls.__module__ + "."
                                + cls.__name__ + "." + methodName + "\n")
                    else:
                        if isinstance(cls.template_doc, str):
                            f.write("-- @description " + cls.template_doc + "\n")
                        else:
                            sys.exit("MADlib Test Error: template_doc must be a string in" +
                                     cls.__module__ + "." + cls.__name__)
                            
                    if add_flag is False:
                        f.write("-- @skip ... by " + cls.__module__ + "." + 
                                cls.__name__ + " according to " + skip_name + "\n")
                        
                    print(methodName + " ............ test case file created")
                    
                    cls._write_params(f, x)
                    f.write("\n")
                    f.write(methodQuery)

            # Call external script to compute the result
            # right now, only support R
            # But it is very easy to add support for other softwares
            if r_ans:
                if os.path.exists(r_script):
                    call_R_script(r_script, ans_dir, methodName, x)
                elif os.path.exists("./" + r_script):
                    call_R_script("./" + r_script, ans_dir, methodName, x)
                else:
                    r_path = os.path.join(ans_dir, r_script)
                    call_R_script(r_path, ans_dir, methodName, x)
                print(cls.__name__ + "." + methodName + " ......... Answer created")
                
        # ------------------------------------------------
        # create test case files
        if cls.create_case_ or (cls.create_ans_ and r_ans):
            makeTestClosure = makeTest
    
            kwargs = {}
            for key, value in template_vars.iteritems():
                if not isinstance(value, list):
                    kwargs[key] = value
                else:
                    def makefunc (key, values, f):
                        def doit (k):
                            for v in values:
                                k[key] = v
                                f(k)
                        return doit
                    makeTestClosure = makefunc(key, value, makeTestClosure)
            
            makeTestClosure(kwargs)

        if ((not cls.create_case_ and not r_ans) or
            (cls.create_ans_ and (not r_ans))): # if R has already created answers, stop
            # read files to create test cases
            return super(MADlibTestCase, cls).loadTestsFromTestCase()
        else:
            return []

    # ----------------------------------------------------------------
        
    def __init__ (self, methodName):
        super(MADlibTestCase, self).__init__(methodName)
        
    # ----------------------------------------------------------------
        
    def _run_test (self, sql_file, ans_file):
        """
        (1) Create a SQL wcript for the query
        (2) Run the SQL script using psql to produce the result file
        (3) Compare the result file to the expected answer file
        """
        sql_resultfile = os.path.join(self.get_out_dir(),
                                      os.path.basename(sql_file) + ".out")

        # create the output of SQL script
        db = self.__class__.db_settings_
        PSQL1.run_sql_file(sql_file, out_file = sql_resultfile,
                           dbname = db["dbname"],
                           username = db["username"],
                           password = db["userpwd"],
                           host = db["host"],
                           port = db["port"],
                           PGOPTIONS = db["pg_options"],
                           psql_options = db["psql_options"])

        # First run to create the baseline file
        if self.__class__.create_ans_:
            shutil.copyfile(sql_resultfile, ans_file)
            os.remove(sql_resultfile)
            print "Answer file was created"
            return True

        return self.validate(sql_resultfile, ans_file)
 
    # ----------------------------------------------------------------

    def validate (self, sql_resultfile, answerfile):
        # Check that the answer file exists
        self.assertTrue(os.path.exists(answerfile))

        # Compare actual result to the answer
        return Gpdiff.are_files_equal(sql_resultfile, answerfile)


        
