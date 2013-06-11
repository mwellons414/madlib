## MADlib Tests for summary
from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import mean_squared_error
from madlib.src.test_utils.utils import read_sql_result
from madlib.src.test_utils.utils import string_to_array
from madlib.src.test_utils.utils import modified_Gpdiff
from madlib.src.test_utils.utils import _get_argument_expansion
from madlib.src.test_utils.get_dbsettings import get_schema_testing
import re
import sys

## -- Input test cases ---------------------------------------------------------
class SummaryInputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    template = """
          set client_min_messages to error;
          select * from
          {schema_madlib}.summary(
              {dataset},
              {tbl_output},
              {target_cols},
              {grouping_cols},
              {get_distinct},
              {get_quartiles},
              {ntile_array},
              {how_many_mfv},
              {get_estimates}
          );
              """
    ans_dir = "expected_input"
    template_method = "summary_input_test_{incr_}"
    template_doc = "Input tests for Sumary"

    argument_dict = dict(
                          dataset=["NULL", "",
                                    "'" + get_schema_testing()
                                        + ".summary_empty_table'"]
                         ,tbl_output = ["NULL", "'-1'"]
                         ,target_cols = ["'non_existing_col'", "'-1'",
                                          "'temperature, non_existing_col'"]
                         ,grouping_cols = ["'non_existing_col'", "'-1'",
                                          "'temperature, non_existing_col'"]
                         ,ntile_array = ["ARRAY[-1, 0.1, 1.0]", "ARRAY[]", "ARRAY[-10]"]
                         ,how_many_mfv = ["NULL", "0", "-10"]
                    )
    argument_defaults = dict(
                          dataset = "'" + get_schema_testing() + ".dt_golf'"
                         ,tbl_output = "'_mdadlib_input_test_summary_output_'"
                         ,target_cols = "NULL"
                         ,grouping_cols = "NULL"
                         ,get_distinct = "True"
                         ,get_quartiles = "True"
                         ,ntile_array = "NULL"
                         ,how_many_mfv = 10
                         ,get_estimates = "True"

                       )
    template_vars = _get_argument_expansion(argument_dict, argument_defaults)

    # Gpdiff cannot ignore the path name in lines with INFO
    # but it can ignore the different path name in lines with ERROR
    def validate(self, sql_resultfile, answerfile):
        modified_Gpdiff(sql_resultfile, answerfile)
# -------------------------------------------------------------------------
