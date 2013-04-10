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

    # ----------------------------------------------------------------
    
    @classmethod
    def loadTestsFromTestCase(cls):
        """
        @param cls The child class 
        """
        # Ensure we pickup the variables from our child class
        template        = cls.template
        template_method = cls.template_method
        template_doc    = cls.template_doc
        template_vars   = cls.template_vars
        
        # XXX: I'm not completely clear why this is necessary, somehow the loadTests ends up
        # being called twice, once for the child class and once from here.  When called from
        # here we need to not die...
        if template is None:
            return []

        assert isinstance(template,str)
        assert isinstance(template_method,str)

        tests = []

        print "loading tests from test case"

        # Also create our "Template" test cases
        def makeTest (x):
            methodName = TINCTestLoader.testMethodPrefix + template_method.format(**x)
            methodDoc  = template_doc.format(**x)
            methodQuery = template.format(**x)
            tests.append(cls(methodName, methodQuery, methodDoc, **x))
            
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
        
        return tests

    # ----------------------------------------------------------------
        
    def __init__ (self, methodName, methodQuery=None, methodDoc=None, **args):

        if methodQuery:
            def generatedTestFunction (myself):
                myself.__runquery(methodName, methodQuery, **args)
            generatedTestFunction.__doc__ = methodDoc
            method = new.instancemethod(generatedTestFunction, self, self.__class__)
            self.__dict__[methodName] = method

        super(MADlibTemplateTestCase,self).__init__(methodName)

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

        # Create an artifact of the SQL we are going to run
        with open(sql_inputfile, 'w') as f:  f.write(methodQuery)

        # create the output of SQL script
        PSQL.run_sql_file(sql_inputfile, out_file = sql_resultfile,
                dbname = args["dbname"], username = args["username"],
                password = args["password"], host = args["host"],
                port = args["port"])

        self.assertTrue(self.validate(sql_resultfile, answerfile,
                                      source_dir = source_dir, **args))
 
    # ----------------------------------------------------------------

    def validate (self, sql_resultfile, answerfile, **args):
        # Check that the answer file exists
        self.assertTrue(os.path.exists(answerfile))

        # Compare actual result to the answer
        self.assertTrue(Gpdiff.are_files_equal(resultfile, answerfile))


        
