
## MADlib Tests for linear regression
## For learning tinc

from src.template.madlib_test import MADlibTestCase
from src.test_utils.utils import unique_string
from src.test_utils.utils import string_to_array
from src.test_utils.utils import mean_squared_error
from src.test_utils.utils import read_sql_result
import os
import re
import sys

# ------------------------------------------------------------------------

run_sql = """
          select {schema_madlib}.linregr_train(
              '{schema_testing}.{dataset}',
              '{tbl_output}',
              '{y}', '{x}',
              NULL,
              {hetero});
          select coef from {tbl_output};
          drop table if exists {tbl_output};
          """

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class LinregrOutputTestCase (MADlibTestCase):
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
    sql_dir = "linregr_sql"
    out_dir = "linregr_result"
    ans_dir = "linregr_expected"

    skip_file = "linregr_skip.py"
    
    template_method = "linregr%{dataset}%{hetero}"

    template_doc = "This is for output tests of linear regression with heteroskedasticity"

    template_vars = dict(
        # These names are not hard-coded
        tbl_output = unique_string(),
        dataset = ["lin_auto_mpg_oi", "lin_auto_mpg_wi"],
        hetero = ["TRUE", "FALSE"],
        x = "x",
        y = "y")

    template = run_sql

    # ----------------------------------------------------------------
    # The following class variables are defined only for this test
    # One can use any names here
    # ----------------------------------------------------------------
    # Since all R result is in one file
    # We just need to read it once
    r_resultfile = "linregr_test2.ans"
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

        # read the R result file only once
        # because all R results are in one file
        if self.__class__.Rresults is None:
            self.__class__.Rresults = self.read_Rresults(R_resultfile)

        args = sql_result["madlib_params"]
        dataset = args["dataset"].lower()
        hetero = args["hetero"].lower()
        r_result = self.__class__.Rresults[dataset][hetero]["coef"]

        sql_coef = self.get_coef(sql_result["result"])

        return mean_squared_error(sql_coef, r_result) < 1e-6

# ------------------------------------------------------------------------

    def get_coef (self, result):
        """
        Just extract the coefficients
        """
        for line in result:
            s = re.match(r"^[^\{]*\{([^\}]*)\}", line)
            if s is not None:
                try:
                    res = map(float, string_to_array(s.group(1)))
                except:
                    sys.exit("Linregr Output Test Error: The array cannot be converted to float!")
                if res is None:
                    sys.exit("Linregr Output Test Error: The array cannot be converted to float!")
                return res

    def read_Rresults (self, resultFile):
        """
        Read R results from the answer file.
        Read only once for all the tests
        """
        count = 0
        res = dict()
        with open(resultFile, "r") as f:
            for line in f:
                line = line.strip("\n").lower()
                count += 1
                if count == 1:
                    current_dataset = line
                    if current_dataset not in res.keys():
                        res[current_dataset] = dict()
                elif count == 2:
                    current_hetero = line
                    res[current_dataset][line] = dict()
                elif count == 3:
                    res[current_dataset][current_hetero]["coef"] = \
                                            map(float, string_to_array(line))
                elif line == "":
                    count = 0 # reset count
        return res

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class LinregrInputTestCase (MADlibTestCase):
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
    sql_dir = "linregr_sql_input"
    out_dir = "linregr_result_input"
    ans_dir = "linregr_expected_input"

    # use a different name convention from the above example
    template_method = "linregr_input_test_{incr_}"

    # doc does not seem to be important
    template_doc = "This is for input tests of linear regression with heteroskedasticity"

    template_vars = dict(
        # These names are not hard-coded

        # I really want to use unique_string as the output table name
        # to avoid possible name conflict.
        # However, we would get different table names in answer files
        # and the result files. And a simple file diff will give
        # False.
        # Two solutions: (1) use a complicate diff function, which
        # does not compare output_table name, or (2) Just use
        # a fixed name, and don't forget to drop the table in run_sql
        # (2) is much easier. We use (2) here
        tbl_output = "__madlib_temp_40418089_1365619947_6556506__",

        dataset = ["lin_auto_mpg_oi", "lin_auto_mpg_wi"],
        hetero = ["TRUE", "FALSE"],
        x = "NULL",
        y = "-1"
    )

    template = run_sql
        
