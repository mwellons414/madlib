'''
MADlibTemplateTestCase is a subclass of GPDBTestCase that provides basic 
cababilities to run a templated SQL statement with substitution rules.

For any list parameters passed as "template_vars" it will iterate through 
all combinations
of parameters and generate a separate test case for each combination.
'''

from madlib.src.template.sql import MADlibSQLTestCase
from madlib.src.template.lib import PSQL1
from madlib.src.test_utils.get_dbsettings import get_dbsettings
from madlib.src.test_utils.utils import call_R_script
from tinctest import TINCTestLoader
from madlib.src.test_utils.utils import biprint
from tinctest.lib import Gpdiff
from madlib.src.template.class_utils import make_sure_path_exists
from madlib.src.template.class_utils import get_env_flag
from madlib.src.template.class_utils import get_ext_ans
from madlib.src.template.class_utils import get_skip
from madlib.src.template.class_utils import clean_dir
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
    sql_dir_head    = "sql_" # store the sql command executed
    out_dir_head    = "result_" # output folder
    ans_dir         = "expected" # expected results
    template        = None  
    template_method = None # method name, controls the file name 
    template_doc    = ""    
    template_vars   = {}
    skip_file = None # "skip.py"
    skip = []
    create_ans_ = False
    create_case_ = False
    db_settings_ = get_dbsettings("MADlibTestCase", "madlib")
    schema_madlib = db_settings_["schema_madlib"]
    schema_testing = db_settings_["schema_testing"]
    reserved_keywords_ = ["incr_", "schema_madlib", "schema_testing"]

    # If you want to use fiel names like "linregr_input_test_{incr}",
    # increse incr for every test, which is done in the super class
    # This number is used for file name
    # to avoid putting very long arguments in the file name
    incr_ = 0 # name is hard-coded

    # ----------------------------------------------------------------

    @classmethod
    def dbKind (cls):
        """
        greenplum or postgres
        """
        return cls.db_settings_["kind"]

    # ----------------------------------------------------------------
        
    @classmethod
    def dbVers (cls):
        """
        get the version number
        """
        m = re.search(r"^(\d+\.\d+\.\d+)", cls.db_settings_["version"])
        return m.group(1)
        
    # -----------------------------------------------------------------

    @classmethod
    def _make_sure_path_exists (cls, path):
        make_sure_path_exists (cls, path)

    # -----------------------------------------------------------------

    @classmethod
    def _get_env_flag (cls, flag, origin = False):
        """
        Get the environment variable for
        creating case or answer file
        """
        return get_env_flag (cls, flag, origin)

    # -----------------------------------------------------------------

    @classmethod
    def _get_ext_ans (cls, flag):
        """
        Get the environment variable for
        creating answer file using
        external script, which takes in
        parameters and compute the results
        """
        return get_ext_ans (cls, flag)

    # ----------------------------------------------------------------

    @classmethod
    def _validate_vars (cls):
        """
        To ensure that the usre provided template_vars
        does not contain the keywords
        """
        if type(cls.template_vars) == type(dict()):
            cls.template_vars = [cls.template_vars]
        elif type(cls.template_vars) == type([]):
            pass
        else:
            sys.exit("MADlib Test Error: template_vars must be a dict or an array of dict !")
        for template_dict in cls.template_vars:
            if type(template_dict) != type(dict()):
                sys.exit("MADlib Test Error: template_vars must be a dict or an array of dict !!")
            anyMatch = any(key in cls.reserved_keywords_ \
                           for key in template_dict.keys())
            if anyMatch:
                biprint("MADlib Test Error: template_vars should not use any of the following keywords:")
                biprint(cls.reserved_keywords_)
                sys.exit("Testcase is stopping for " + cls.__module__ + "." + cls.__name__ + " !")
        return None

    # ----------------------------------------------------------------

    @classmethod
    def _get_skip (cls):
        """
        Get skip list
        """
        return get_skip (cls)
 
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
        ## template_vars   = cls.template_vars

        if template_method is None or template is None:
            # biprint("MADlib Test Error: " + cls.__module__ + "." + cls.__name__ + " !")
            return []
       
        cls.create_case_ = cls._get_env_flag("CREATE_CASE")
        cls.create_ans_ = cls._get_env_flag("CREATE_ANS")
        (r_ans, r_script) = cls._get_ext_ans("R_ANS")

        # validate cls template_vars
        cls._validate_vars()

        for template_dict in cls.template_vars:
            template_dict.update(schema_madlib = cls.db_settings_["schema_madlib"],
                                 schema_testing = cls.db_settings_["schema_testing"])
            
        assert isinstance(template,str)
        assert isinstance(template_method,str)

        biprint("loading tests from test case")

        source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))
        ans_dir = os.path.join(source_dir, cls.ans_dir)
        sql_dir = os.path.join(os.path.dirname(ans_dir),
                               cls.sql_dir_head + cls.__name__)
        out_dir = os.path.join(os.path.dirname(ans_dir),
                               cls.out_dir_head + cls.__name__)
        cls.ans_dir = ans_dir
        cls.sql_dir = sql_dir
        cls.out_dir = out_dir

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
                    if methodDoc == "" or methodDoc is None:
                        f.write("-- @description " + cls.__module__ + "."
                                + cls.__name__ + "." + methodName + "\n")
                    else:
                        if isinstance(methodDoc, str):
                            f.write("-- @description " + methodDoc + "\n")
                        else:
                            sys.exit("MADlib Test Error: template_doc must be a string in" +
                                     cls.__module__ + "." + cls.__name__)
                            
                    if add_flag is False:
                        f.write("-- @skip ... by " + cls.__module__ + "." + 
                                cls.__name__ + "\n")
                        
                    biprint(methodName + " ............ test case file created")
                    
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
                biprint(cls.__name__ + "." + methodName + " ......... Answer created")
                
        # ------------------------------------------------
        # create test case files
        if cls.create_case_ or (cls.create_ans_ and r_ans):
            if cls.create_case_:
                clean_dir(sql_dir)

            if cls.create_ans_:
                clean_dir(out_dir)
            
            skip = cls._get_skip()
                        
            for template_dict in cls.template_vars:
                makeTestClosure = makeTest
                kwargs = {}
                for key, value in template_dict.iteritems():
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
        
    def __init__ (self, methodName, sql_file = None, db_name = None):
        super(MADlibTestCase, self).__init__(methodName, sql_file,
                                             self.__class__.db_settings_["dbname"])
        
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
            biprint("Answer file was created")
            return True

        return self.validate(sql_resultfile, ans_file)
 
    # ----------------------------------------------------------------

    def validate (self, sql_resultfile, answerfile):
        # Check that the answer file exists
        self.assertTrue(os.path.exists(answerfile))

        # Compare actual result to the answer
        return Gpdiff.are_files_equal(sql_resultfile, answerfile)


        
