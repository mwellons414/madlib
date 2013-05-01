
## MADlib Tests for correlation
## For learning tinc

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import string_to_array
from madlib.src.test_utils.utils import mean_squared_error
from madlib.src.test_utils.utils import read_sql_result
import os
import re
import sys

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class CorrelationOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
      set client_min_messages to error;
      select output_table, row_count from
      {schema_madlib}.correlation(
          '{schema_testing}.{dataset}',
          '{tbl_output}');
      select * from {tbl_output} order by column_position;
      drop table if exists {tbl_output};
      """
    # ----------------------------------------------------------------
    # These class variable names are hard-coded and used by
    # template/madlib_test.py.
    # One should not change them
    # It is possible to make them un-hard-coded
    # But that does not seem to bring us much.
    # ----------------------------------------------------------------
    # Required by superclass
    sql_dir = "sql_output"
    out_dir = "result_output"
    ans_dir = "expected_output"

    template_method = "correlation%{dataset}"
    template_doc = "This is for output tests of correlation."

    template_vars = dict(
        dataset = ["dt_golf"], # , "dt_kddcup"],
        tbl_output = unique_string())

    template = run_sql

    def validate (self, sql_resultfile, answerfile):
        result = read_sql_result(sql_resultfile)
        answer = read_sql_result(answerfile)
        res_coef = self.get_corr_coef(result["result"])
        ans_coef = self.get_corr_coef(answer["result"])
        return mean_squared_error(res_coef, ans_coef) < 1e-6

    def get_corr_coef(self, result):
        coef_str = ''
        for line in result:
            if(re.match('\d+', line.strip())):
                coef_str += line
        coef_str = re.sub('[^0-9.]+', ' ',coef_str)
        coef_str = re.sub('\s+', ' ',coef_str).strip()
        coef = []
        for item in coef_str.split(' '):
            coef.append(float(item))
        return coef

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class CorrelationInputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
          set client_min_messages to error;
          select output_table, row_count from
          {schema_madlib}.correlation(
              {dataset},
              {tbl_output},
              {target_cols});
          """
    # ----------------------------------------------------------------
    # These class variable names are hard-coded and used by
    # template/madlib_test.py.
    # One should not change them
    # It is possible to make them un-hard-coded
    # But that does not seem to bring us much.
    # ----------------------------------------------------------------
    # Required by superclass
    sql_dir = "sql_input"
    out_dir = "result_input"
    ans_dir = "expected_input"

    skip_file = "corr_skip.py"

    template_method = "correlation_input_test_{incr_}"
    template_doc = "This is for output tests of correlation."

    template_vars = dict(
        dataset = [
            "'" + MADlibTestCase.schema_testing + ".dt_golf'",
            "'" + MADlibTestCase.schema_testing + ".non_existing_table'",
            "NULL", "''", "'-1'"],
        tbl_output = [
            "'__madlib_temp_40418089_1365619947_6556506__'",
            "NULL", "''"],
        target_cols = [
            "'non_existing_col'",
            "'windy, outlook'",
            "'humidity, temperature'",
            "NULL", "''"])
    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

