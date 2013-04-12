'''
MADlibTemplateTestCase is a subclass of GPDBTestCase that provides basic 
cababilities to run a templated SQL statement with substitution rules.

For any list parameters passed as "template_vars" it will iterate through 
all combinations
of parameters and generate a separate test case for each combination.
'''

from tinctest.models.gpdb import GPDBTestCase
from tinctest import TINCTestLoader
from tinctest.lib import PSQL, Gpdiff
import new
import os
import sys
import shutil

# ------------------------------------------------------------------------
# Use environment variables to control the behavior:
#
# CREATE_CASE   to create case files
# CREATE_ANS    to create answer files (mainly for input test cases)
# DB_CONFIG     to pick a database configuration from sys_settings.dbsettings
# ------------------------------------------------------------------------

class MADlibTemplateTestCase (GPDBTestCase):
    """
    Abstract class for running templated SQL, subclasses must define the template
    """
    # The following variables should be provided by subclass
    schema_madlib   = "madlib"
    sql_dir         = "" # store the sql command executed
    out_dir         = "" # output folder
    ans_dir         = "" # expected results
    template        = None  
    template_method = None # method name, controls the file name 
    template_doc    = ""    
    template_vars   = {}
    skip = None
    reserved_keywords = ["_incr", "_create_ans", "_create_case", "_db_settings"]

    # If you want to use fiel names like "linregr_input_test_{incr}",
    # increse incr for every test, which is done in the super class
    # This number is used for file name
    # to avoid putting very long arguments in the file name
    incr = 0 # name is hard-coded

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

    # ----------------------------------------------------------------

    # @classmethod
    # def get_skips (cls):
    #     """
    #     Get the skip file contents
    #     """
    #     source_file = sys.modules[cls.__module__].__file__
    #     source_dir = os.path.dirname(source_file)
    #     if os.environ.has_key("SKIP"):
    #         value = os.environ.get("SKIP").split(":")
            
    #     return False

    # ----------------------------------------------------------------

    @classmethod
    def _validate_vars (cls, template_vars, keywords):
        """
        To ensure that the usre provided template_vars
        does not contain the keywords
        """
        anyMatch = any(key in keywords for key in template_vars.keys())
        if anyMatch:
            print("template_vars should not use any of the following keywords:")
            print(keywords)
            sys.exit("Testcase is stopping ...")
        return None

    # ----------------------------------------------------------------

    @classmethod
    def _get_dbsettings (cls):
        """
        Get the database settings from environment
        """
        db = dict(dbname = None, username = None, password = None,
                  host = None, port = None) # default values
        import sys_settings.dbsettings
        if os.environ.has_key("DB_CONFIG"):
            value = os.environ.get("DB_CONFIG")
            try:
                user_set = getattr(sys_settings.dbsettings, value)
            except:
                sys.exit("No such database settings!")
        else:
            user_set = sys_settings.dbsettings.default
        for key in user_set.keys():
            db[key] = user_set[key]
        return db
    
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

        # validate cls template_vars
        MADlibTemplateTestCase._validate_vars(template_vars,
                                              MADlibTemplateTestCase.reserved_keywords)
        
        template_vars.update(_db_settings = MADlibTemplateTestCase._get_dbsettings())
        template_vars.update(_create_case = MADlibTemplateTestCase._get_env_flag("CREATE_CASE"),
                             _create_ans = MADlibTemplateTestCase._get_env_flag("CREATE_ANS"))
        skip = cls.skip
            
        # XXX: I'm not completely clear why this is necessary, somehow the loadTests ends up
        # being called twice, once for the child class and once from here.  When called from
        # here we need to not die...
        if template is None:
            return []

        assert isinstance(template,str)
        assert isinstance(template_method,str)
        tests = []

        print "loading tests from test case"

        source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(source_file)

        # ------------------------------------------------
        # Also create our "Template" test cases
        def makeTest (x):
            cls.incr += 1
            x["incr"] = cls.incr
            methodName = TINCTestLoader.testMethodPrefix + template_method.format(**x)
            methodDoc  = template_doc.format(**x)
            methodQuery = template.format(**x)

            ## Skip a test case
            add_flag = True
            if skip is not None:
                for case in skip:
                    eq = True
                    for key in case.keys():
                        if x[key].lower() != case[key].lower():
                            eq = False
                            break
                    if eq:
                        add_flag = False
                        break

            if add_flag:
                tests.append(cls(methodName, methodQuery, methodDoc, **x))
            else:
                print(cls.__name__ + "." + methodName + " ........... skipped")

            # Create an artifact of the SQL we are going to run
            # if "create_case" in args.keys() and args["create_case"]:
            if x["_create_case"]:
                sql_inputfile = os.path.join(source_dir, cls.sql_dir,
                                             methodName + ".sql")
                with open(sql_inputfile, 'w') as f:
                    if add_flag is False:
                        f.write("-- @skip Skip this test")
                    f.write(methodQuery)
        # ------------------------------------------------
            
        makeTestClosure = makeTest

        kwargs = {}
        for key, value in template_vars.iteritems():
            if not isinstance(value, list) or key == "skip":
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

        return tests

    # ----------------------------------------------------------------
        
    def __init__ (self, methodName, methodQuery=None, methodDoc=None, **args):

        if methodQuery:
            def generatedTestFunction (myself):
                myself.__runquery(methodName, methodQuery, **args)
            generatedTestFunction.__doc__ = methodDoc
            method = new.instancemethod(generatedTestFunction, self, self.__class__)
            self.__dict__[methodName] = method

        super(MADlibTemplateTestCase, self).__init__(methodName)

    # ----------------------------------------------------------------
        
    def __runquery (self, methodName, methodQuery, **args):
        """
        (1) Create a SQL wcript for the query
        (2) Run the SQL script using psql to produce the result file
        (3) Compare the result file to the expected answer file
        """
        source_file = sys.modules[self.__class__.__module__].__file__
        source_dir = os.path.dirname(source_file)
        sql_inputfile = os.path.join(source_dir, self.__class__.sql_dir,
                                     methodName + ".sql")
        sql_resultfile = os.path.join(source_dir, self.__class__.out_dir,
                                      methodName + ".sql.out")
        answerfile = os.path.join(source_dir, self.__class__.ans_dir,
                                  methodName + ".ans")

        # create the output of SQL script
        PSQL.run_sql_file(sql_inputfile, out_file = sql_resultfile,
                          dbname = args["_db_settings"]["dbname"],
                          username = args["_db_settings"]["username"],
                          password = args["_db_settings"]["password"],
                          host = args["_db_settings"]["host"],
                          port = args["_db_settings"]["port"])

        # First run to create the baseline file
        if args["_create_ans"]:
            shutil.copyfile(sql_resultfile, answerfile)
            os.remove(sql_resultfile)
            print "Answer file was created"
            return True

        return self.assertTrue(self.validate(sql_resultfile, answerfile,
                                             source_dir = source_dir, **args))
 
    # ----------------------------------------------------------------

    def validate (self, sql_resultfile, answerfile, **args):
        # Check that the answer file exists
        self.assertTrue(os.path.exists(answerfile))

        # Compare actual result to the answer
        return Gpdiff.are_files_equal(sql_resultfile, answerfile)


        
