
## MADlib Tests for linear regression
## For learning tinc

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import string_to_array
from madlib.src.test_utils.utils import relative_mean_squared_error
from madlib.src.test_utils.utils import read_sql_result
from madlib.src.test_utils.utils import parse_all_R_output
from madlib.src.test_utils.utils import parse_single_SQL_output
from madlib.src.test_utils.utils import _get_argument_expansion
from madlib.src.test_utils.get_dbsettings import get_schema_testing
import os
import re
import sys

# ------------------------------------------------------------------------

output_test_sql = """
          select {schema_madlib}.robust_variance(
              '{schema_testing}.{dataset}_wi',
              '{tbl_output}', 'linear',
              {y}, {x});
          select coef from {tbl_output};
          select std_err from {tbl_output};
          select t_stats from {tbl_output};
          select p_values from {tbl_output};
          drop table if exists {tbl_output};
          """

input_test_sql = """
          select {schema_madlib}.robust_variance(
              '{schema_testing}.{dataset}_wi',
              '{tbl_output}', 'linear',
              {y}, {x});
          drop table if exists {tbl_output};
          """


ALL_DATASETS = [
"lin_auto_mpg",
"lin_communities",
"lin_flare",
"lin_forestfires",
"lin_housing",
"lin_imports_85",
"lin_machine",
"lin_ornstein",
"lin_parkinsons_updrs",
"lin_servo",
"lin_slump",
"lin_winequality_red",
"lin_winequality_white"]


## NOTICE:
# The dataset "lin_parkinsons_updrs" is an expected failure dataset

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class RobustLinregrOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    # ----------------------------------------------------------------
    # These class variable names are hard-coded and used by
    # template/madlib_test.py.
    # One should not change them
    # It is possible to make them un-hard-coded
    # But that does not seem to bring us much.
    # ----------------------------------------------------------------
    # Required by superclass
    ans_dir = "expected_output"

    # skip_file = "robust_linregr_skip.py"
    
    template_method = "robust_linregr%{dataset}"

    template_doc = "This is for output tests of robust linear regression"

    template_vars = dict(
        # These names are not hard-coded
        tbl_output = unique_string(),
        dataset = ALL_DATASETS, 
        x = "'x'",
        y = "'y'")

    template = output_test_sql

    # ----------------------------------------------------------------
    # The following class variables are defined only for this test
    # One can use any names here
    # ----------------------------------------------------------------
    # Since all R result is in one file
    # We just need to read it once
    r_resultfile = "robust_linregr_test.ans"
    Rresults = None

    # ----------------------------------------------------------------
    # One only needs to implement the result validation function
    def validate (self, sql_resultfile, answerfile):
        """
        Compare the result of SQL with answer file
        Matching parameters in args
        """
        sql_result = read_sql_result(sql_resultfile)
 
        # In this test, we use a single R result file, which
        # is source_dir/ans_dir/r_result. More parameters
        # are passed in by **args
        R_resultfile = os.path.join(self.get_source_dir(),
                                    self.get_ans_dir(),
                                    self.__class__.r_resultfile)

        # Read the R result file only once
        # Outputs must be in the same order in SQL, R and this ARRAY 
        # The dictionary logs which positions contain which options/parameters
        # -------------------------------------------------------------------- 
        options_dict = {} 
        results_dict = {} 
        # Indexing starts at 1 (we are computer scientists)
        options_dict["dataset"] = 0    
        results_dict["coef"] = 1          
        results_dict["std_err"] = 2          
        results_dict["t_stats"] = 3          
        results_dict["p_values"] = 4          
        if self.__class__.Rresults is None:
            self.__class__.Rresults = parse_all_R_output(R_resultfile \
                                                       , options_dict \
                                                       , results_dict)

        # Look through the SQL files to parse all the answers 
        # This script assumes that the SQL and R answers are in the same order 
        # -------------------------------------------------------------------- 
        args = sql_result["madlib_params"]
        dataset = args["dataset"].lower()
        options = tuple([dataset]) # Must be hashable
        r_results = self.__class__.Rresults[options]
        sql_results = parse_single_SQL_output(sql_result["result"], results_dict)
        
        flag = True
        failed = []
        # Keep track of failed outputs 
        # -------------------------------------------------------------------- 
        for params in results_dict:
            if relative_mean_squared_error(sql_results[params], r_results[params]) > 1e-3:
              failed.append(params)
              flag = False  
        if flag == False:
            print "Failed in %s" % ' '.join(failed)
        return flag 


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class RobustLinregrInputTestCase (MADlibTestCase):
  """
  Run input tests
  """
  # ----------------------------------------------------------------
  # These class variable names are hard-coded and used by
  # template/madlib_test.py.
  # One should not change them
  # It is possible to make them un-hard-coded
  # But that does not seem to bring us much.
  # ----------------------------------------------------------------
  # Example 1:
  ans_dir = "expected_input" if MADlibTestCase.dbKind() == "greenplum" \
            else "expect_input_pg"


  # use a different name convention from the above example
  template_method = "robust_linregr_input_test_{incr_}"

  # doc does not seem to be important
  template_doc = "This is for input tests of linear robust regression "

  arg_dict = dict(
      tbl_output = [],
      dataset = [], 
      x = ["'wrong_col_name'", "NULL", "wrong_type_name"],
      y = ["'wrong_col_name'", "NULL", "wrong_type_name"],
  )
  default_arg_dict = dict(
      tbl_output = '__madlib_temp_40418089_1365619947_6556506__',
      dataset = "lin_auto_mpg",
      x = "'x'",
      y = "'y'",
  )

  template_vars = _get_argument_expansion(arg_dict, default_arg_dict)
  template = input_test_sql
  skip_file = "robust_linregr_skip.py"

  # One only needs to implement the result validation function
  def validate (self, sql_resultfile, answerfile):
    """
    Compare the result of SQL with answer file
    Matching parameters in args
    """
    sql_result = read_sql_result(sql_resultfile)
    args = sql_result["madlib_params"]
    errMessage = self.get_errMessage(sql_result["result"])
    expectedResults = self.get_expectedInput(answerfile)
    return errMessage == expectedResults

  def get_expectedInput (self, resultFile):
    #Get the expected results
    message = None
    results = open(resultFile, 'r').readlines()
    for line in results:
      pattern = ".*ERROR\s*(.*)"
      s = re.match(pattern, line)
      if(s != None):
        message = s.group(1)
        break
    return message
        
  def get_errMessage (self, result):
    message = None
    for line in result:
      pattern = ".*ERROR\s*(.*)"
      s = re.match(pattern, line)
      if(s != None):
        message = s.group(1)
        break
    return message
