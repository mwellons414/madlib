
## MADlib Tests for correlation
## For learning tinc

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import mean_squared_error
from madlib.src.test_utils.get_dbsettings import get_schema_testing
from tinctest.lib import Gpdiff
from util import read_mem_result_file
from util import read_answer_file
import re
import os

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


class MatrixMemTransOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select 
            {schema_madlib}.matrix_mem_trans(block) as block_t 
        from
            {schema_testing}.{dataset};
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

    template_method = "matrix_mem_trans%{dataset}"
    template_doc = "This is for output tests of in-memory matrix transposition."

    template_vars = dict(dataset = ["matrix_mem_100_200"])

    template = run_sql

    MADlibTestCase.db_settings_["psql_options"] = "-x"

    def validate (self, sql_resultfile, answerfile):
        result = read_mem_result_file(sql_resultfile, 'block_t')
        answer = read_answer_file(answerfile)
        return mean_squared_error(result, answer) < 1e-6

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
class MatrixMemMultOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select 
            {schema_madlib}.matrix_mem_mult(
                block,
                {schema_madlib}.matrix_mem_trans(block)
            ) AS block_square
        from
            {schema_testing}.{dataset};
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

    template_method = "matrix_mem_mult%{dataset}"
    template_doc = "This is for output tests of in-memory matrix multiplication."

    template_vars = dict(dataset = ["matrix_mem_100_200"])

    template = run_sql

    MADlibTestCase.db_settings_["psql_options"] = "-x"

    def validate (self, sql_resultfile, answerfile):
        result = read_mem_result_file(sql_resultfile, 'block_square')
        answer = read_answer_file(answerfile)
        return mean_squared_error(result, answer) < 1e-6

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
