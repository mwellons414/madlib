
## MADlib Tests for linear regression
## For learning tinc

from template.madlib_test import MADlibTemplateTestCase
from template.utils import unique_string
from template.utils import string_to_array
from template.utils import mean_squared_error
import os
import sys

# ------------------------------------------------------------------------

run_sql = """
          select {schema_madlib}.linregr_train(
              '{test_schema}.{dataset}',
              '{tbl_output}',
              '{y}', '{x}',
              NULL,
              {hetero});
          select coef from {tbl_output};
          drop table if exists {tbl_output};
          """

# ------------------------------------------------------------------------

class LinregrOutputTestCase (MADlibTemplateTestCase):
    """
    Run templated SQL tests
    """
    sql_dir = "linregr_sql"
    out_dir = "linregr_result"
    ans_dir = "linregr_expected"

    # Required by superclass
    template_method = "linregr%{dataset}%{hetero}"
    template_doc = ""
    template_vars = dict(
        schema_madlib = "madlib",
        test_schema = "madlibtestdata",
        tbl_output = unique_string(),
        dataset = ["lin_auto_mpg_oi", "lin_auto_mpg_wi"],
        hetero = ["TRUE", "FALSE"],
        r_resultfile = "linregr_test.ans",
        x = "x",
        y = "y",
        dbname = "qianh1", username = "qianh1",
        password = None, host = "localhost", 
        port = None # use the port provided by environment
    )

    template = run_sql

    # Since all R result is in one file
    # We just need to read it once
    Rresults = None

    # Skip some parameter combinations
    skip = [["lin_auto_mpg_oi", "TRUE"],
            ["lin_auto_mpg_wi", "FALSE"]]

    def validate (self, sql_resultfile, answerfile, **args):
        """
        Compare the result of SQL with answer file
        Matching parameters in args
        """
        
        with open(sql_resultfile, "r") as f:
            for line in f:
                # Look a line that looks like '^ {...}$'
                if line.startswith(' {') and line.endswith('}\n'):
                    sql_result = map(float, string_to_array(line[2:-2]))
                    break # only compare coef, the first array

        # In this test, we use a single R result file, which
        # is source_dir/ans_dir/r_result. More parameters
        # are passed in by **args
        R_resultfile = os.path.join(args["source_dir"],
                                    self.__class__.ans_dir,
                                    args["r_resultfile"])

        # read the R result file only once
        # because all R results are in one file
        if self.__class__.Rresults is None:
            self.__class__.Rresults = read_Rresults(R_resultfile)
 
        dataset = args["dataset"].lower()
        hetero = args["hetero"].lower()
        r_result = self.__class__.Rresults[dataset][hetero]["coef"]

        return mean_squared_error(sql_result, r_result) < 1e-6

# ------------------------------------------------------------------------

def read_Rresults (resultFile):
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
