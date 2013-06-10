
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

class MatrixBlockTransOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_blockize(
            '{schema_testing}.{matrix_in}', 
            {rsize}, {csize},
            '{matrix_in_block}');

        select {schema_madlib}.matrix_block_trans(
            '{matrix_in_block}',
            '{matrix_out_block}');

        select {schema_madlib}.matrix_unblockize(
            '{matrix_out_block}',
            '{matrix_out}');

        select row_vec from {matrix_out} order by row_id;

        drop table if exists {matrix_out};
        drop table if exists {matrix_out_block};
        drop table if exists {matrix_in_block};
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
    template_method = "matrix_block_trans%{matrix_in}"
    template_doc = "This is for output tests of dense matrix (block format) transposition."

    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        rsize = 100, csize = 100,
        matrix_in_block = unique_string(),
        matrix_out_block = unique_string(),
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
class MatrixBlockMultOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_blockize(
            '{schema_testing}.{matrix_in}', 
            {rsize}, {csize},
            '{matrix_in_block}');

        select {schema_madlib}.matrix_block_trans(
            '{matrix_in_block}',
            '{matrix_in_trans_block}');

        select {schema_madlib}.matrix_block_mult(
            '{matrix_in_block}',
            '{matrix_in_trans_block}',
            '{matrix_r_block}');

        select {schema_madlib}.matrix_unblockize(
            '{matrix_r_block}',
            '{matrix_r}');

        select row_vec from {matrix_r} order by row_id;

        drop table if exists {matrix_r};
        drop table if exists {matrix_r_block};
        drop table if exists {matrix_in_trans_block};
        drop table if exists {matrix_in_block};
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
    template_method = "matrix_block_mult%{matrix_in}"
    template_doc = "This is for output tests of dense matrix (block format) multiplication."

    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        rsize = 100, csize = 100,
        matrix_in_block = unique_string(),
        matrix_in_trans_block = unique_string(),
        matrix_r_block = unique_string(),
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

class MatrixBlockInputTestCase1 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_blockize(
            {matrix_in}, {rsize}, {csize}, {matrix_out});
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
    template_method = "matrix_block_input1_{incr_}"
    template_doc = "This is for input tests of matrix_blockize."

    template_vars = []
    template_vars.append(
        dict(
            matrix_in = ["NULL", "''", "'non_existing_input_table'"],
            rsize = '5', 
            csize = '5',
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            rsize = ['-1', '0', 'NULL'],
            csize = '5',
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            rsize = '5',
            csize = ['-1', '0', 'NULL'],
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            rsize = '5',
            csize = '5',
            matrix_out = ['NULL', "''"]
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixBlockInputTestCase2 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_block_trans(
            {matrix_in}, {matrix_out});
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
    template_method = "matrix_block_input2_{incr_}"
    template_doc = "This is for input tests of matrix_block_trans."

    template_vars = []
    template_vars.append(
        dict(
            matrix_in = ["NULL", "''", "'non_existing_input_table'"],
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            matrix_out = ["NULL", "''"]
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixBlockInputTestCase3 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_block_mult(
            {matrix_a}, {matrix_b}, {matrix_r});
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
    template_method = "matrix_block_input3_{incr_}"
    template_doc = "This is for input tests of matrix_block_mult."

    template_vars = []
    template_vars.append(
        dict(
            matrix_a = ["NULL", "''", "'non_existing_input_table'"],
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_a = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            matrix_b = ["NULL", "''", "'non_existing_input_table'"],
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_a = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            matrix_r = ["NULL", "''"]
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixBlockInputTestCase4 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_unblockize(
            {matrix_in}, {matrix_out});

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
    template_method = "matrix_block_input4_{incr_}"
    template_doc = "This is for input tests of matrix_unblockize."

    template_vars = []
    template_vars.append(
        dict(
            matrix_in = ["NULL", "''", "'non_existing_input_table'"],
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'" 
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_block_100_100'",
            matrix_out = ["NULL", "''"]
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

