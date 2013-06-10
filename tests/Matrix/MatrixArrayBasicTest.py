## MADlib Tests for correlation
## For learning tinc

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import mean_squared_error
from madlib.src.test_utils.get_dbsettings import get_schema_testing
from tinctest.lib import Gpdiff
from util import read_array_result_file
from util import read_answer_file
import re
import os

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixArrayTransOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_trans(
            '{schema_testing}.{matrix_in}', 
            '{matrix_out}', true);

        select row_vec from {matrix_out} order by row_id;

        drop table if exists {matrix_out};
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
    template_method = "matrix_array_trans%{matrix_in}"
    template_doc = "This is for output tests of dense matrix (array format) transposition."

    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        matrix_out = unique_string()
    )

    template = run_sql
    MADlibTestCase.db_settings_["psql_options"] = "-x"

    def validate (self, sql_resultfile, answerfile):
        result = read_array_result_file(sql_resultfile)
        answer = read_answer_file(answerfile)
        return mean_squared_error(result, answer) < 1e-6

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixArrayMultOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_mult(
            '{schema_testing}.{matrix_in}', false,
            '{schema_testing}.{matrix_in}', true, 
            '{matrix_r}');

        select row_vec from {matrix_r} order by row_id;

        drop table if exists {matrix_r};
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
    template_method = "matrix_array_mult%{matrix_in}"
    template_doc = "This is for output tests of dense matrix (array format) multiplication."

    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        matrix_r = unique_string()
    )

    template = run_sql
    MADlibTestCase.db_settings_["psql_options"] = "-x"

    def validate (self, sql_resultfile, answerfile):
        result = read_array_result_file(sql_resultfile)
        answer = read_answer_file(answerfile)
        return mean_squared_error(result, answer) < 1e-1

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixArrayTransInputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_trans(
            {matrix_in}, 
            {matrix_out},
            {use_temp_table});
      """
    # ----------------------------------------------------------------
    # These class variable names are hard-coded and used by
    # template/madlib_test.py.
    # One should not change them
    # It is possible to make them un-hard-coded
    # But that does not seem to bring us much.
    # ----------------------------------------------------------------
    # Required by superclass
    ans_dir = "expected_input" if MADlibTestCase.dbKind() == "greenplum" \
              else "expect_input_pg"
    template_method = "matrix_array_trans{incr_}"
    template_doc = "This is for input tests of dense matrix (array format) transposition."

    template_vars = []
    template_vars.append(
        dict(
            matrix_in = ["NULL", "''", "'non_existing_input_table'"],
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_out = ["NULL", "''"],
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'NULL'
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixArrayMultInputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_mult(
            {matrix_a}, {trans_a},
            {matrix_b}, {trans_b},
            {matrix_r});
      """
    # ----------------------------------------------------------------
    # These class variable names are hard-coded and used by
    # template/madlib_test.py.
    # One should not change them
    # It is possible to make them un-hard-coded
    # But that does not seem to bring us much.
    # ----------------------------------------------------------------
    # Required by superclass
    ans_dir = "expected_input" if MADlibTestCase.dbKind() == "greenplum" \
              else "expect_input_pg"
    template_method = "matrix_array_mult{incr_}"
    template_doc = "This is for input tests of dense matrix (array format) multiplication."

    template_vars = []
    template_vars.append(
        dict(
            matrix_a = ["NULL", "''", "'non_existing_input_table'"],
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'",
            trans_a = 'true',
            trans_b = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_a = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_b = ["NULL", "''", "'non_existing_input_table'"],
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'",
            trans_a = 'true',
            trans_b = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_a = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_r = ["NULL", "''"],
            trans_a = 'true',
            trans_b = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_a = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'",
            trans_a = 'NULL',
            trans_b = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_a = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_array_100_100'",
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'",
            trans_a = 'true',
            trans_b = 'NULL'
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
