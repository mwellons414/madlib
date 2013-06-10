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

class MatrixSparseTransOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_sparsify(
            '{schema_testing}.{matrix_in}', 
            '{matrix_in_sparse}', 
            true);

        select {schema_madlib}.matrix_trans(
            '{matrix_in_sparse}', 
            'row_id', 'col_id', 'value',
            '{matrix_in_sparse_trans}',
            true);

        select {schema_madlib}.matrix_densify(
            '{matrix_in_sparse_trans}',
            'row_id', 'col_id', 'value',
            '{matrix_out}', 
            true);

        select row_vec from {matrix_out} order by row_id;

        drop table if exists {matrix_out};
        drop table if exists {matrix_in_sparse_trans};
        drop table if exists {matrix_in_sparse};
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
    template_method = "matrix_sparse_trans%{matrix_in}"
    template_doc = "This is for output tests of sparse matrix transposition."

    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        matrix_in_sparse = unique_string(),
        matrix_in_sparse_trans = unique_string(),
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
class MatrixSparseMultOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_sparsify(
            '{schema_testing}.{matrix_in}', 
            '{matrix_in_sparse}', 
            true);

        select {schema_madlib}.matrix_mult(
            '{matrix_in_sparse}', 
            'row_id', 'col_id', 'value', false,
            '{matrix_in_sparse}', 
            'row_id', 'col_id', 'value', true,
            '{matrix_r}');

        select row_vec from {matrix_r} order by row_id;

        drop table if exists {matrix_r};
        drop table if exists {matrix_in_sparse};
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
    template_method = "matrix_sparse_mult%{matrix_in}"
    template_doc = "This is for output tests of sparse matrix multiplication."

    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        matrix_in_sparse = unique_string(),
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

class MatrixSparseDenseMixMultOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_sparsify(
            '{schema_testing}.{matrix_in}', 
            '{matrix_in_sparse}', 
            true);

        select {schema_madlib}.matrix_mult(
            '{matrix_in_sparse}', 
            'row_id', 'col_id', 'value', false,
            '{schema_testing}.{matrix_in}', 
            NULL, NULL, NULL, true,
            '{matrix_r}');

        select row_vec from {matrix_r} order by row_id;

        drop table if exists {matrix_r};
        drop table if exists {matrix_in_sparse};
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
    template_method = "matrix_sparse_dense_mix_mult%{matrix_in}"
    template_doc = "This is for output tests of sparse and dense matrix multiplication."
    template_vars = dict(
        matrix_in = ["matrix_array_1k_500"], 
        matrix_in_sparse = unique_string(),
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

class MatrixSparseInputTestCase1 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_sparsify(
            {matrix_in}, {matrix_out}, {use_temp_table});
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
    template_method = "matrix_sparse_input1_{incr_}"
    template_doc = "This is for input tests of matrix_sparsify."

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

class MatrixSparseInputTestCase2 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_trans(
            {matrix_in}, {row_id}, {col_id}, {value}, {matrix_out},
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
    template_method = "matrix_sparse_input2_{incr_}"
    template_doc = "This is for input tests of matrix_trans."

    template_vars = []
    template_vars.append(
        dict(
            matrix_in = ["NULL", "''", "'non_existing_input_table'"],
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = ['NULL', "''", "'non_exisiting_rowid'"],
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = ['NULL', "''", "'non_exisiting_colid'"],
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = ['NULL', "''", "'non_exisiting_value'"],
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = ['NULL', "''"],
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'NULL'
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixSparseInputTestCase3 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_densify(
            {matrix_in}, {row_id}, {col_id}, {value}, {matrix_out},
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
    template_method = "matrix_sparse_input3_{incr_}"
    template_doc = "This is for input tests of matrix_densify."

    template_vars = []
    template_vars.append(
        dict(
            matrix_in = ["NULL", "''", "'non_existing_input_table'"],
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = ['NULL', "''", "'non_exisiting_rowid'"],
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = ['NULL', "''", "'non_exisiting_colid'"],
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = ['NULL', "''", "'non_exisiting_value'"],
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = ['NULL', "''"],
            use_temp_table = 'true'
        )
    )
    template_vars.append(
        dict(
            matrix_in = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_id = "'row_id'",
            col_id = "'col_id'",
            value = "'value'",
            matrix_out = "'__madlib_temp_40418089_1365619947_6556506__'", 
            use_temp_table = 'NULL'
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MatrixSparseInputTestCase4 (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;

        select {schema_madlib}.matrix_mult(
            {matrix_a}, {row_a}, {col_a}, {val_a}, {trans_a},
            {matrix_b}, {row_b}, {col_b}, {val_b}, {trans_b},
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
    template_method = "matrix_sparse_input4_{incr_}"
    template_doc = "This is for input tests of matrix_mult."

    template_vars = []
    template_vars.append(
        dict(
            matrix_a = ["NULL", "''", "'non_existing_input_table'"],
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = ['NULL', "''", "'non_exisiting_rowid'"],
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = ['NULL', "''", "'non_exisiting_colid'"],
            val_a = "'value'",
            trans_a = 'true',
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = ['NULL', "''", "'non_exisiting_value'"],
            trans_a = 'true',
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'NULL',
            matrix_b = 
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b = ["NULL", "''", "'non_existing_input_table'"],
            row_b = "'row_id'",
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = ['NULL', "''", "'non_exisiting_rowid'"],
            col_b = "'col_id'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = ['NULL', "''", "'non_exisiting_colid'"],
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_b'",
            val_b = ['NULL', "''", "'non_exisiting_value'"],
            trans_b = 'true',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_b'",
            val_b = "'value'",
            trans_b = 'NULL',
            matrix_r = "'__madlib_temp_40418089_1365619947_6556506__'", 
        )
    )
    template_vars.append(
        dict(
            matrix_a =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_a = "'row_id'",
            col_a = "'col_id'",
            val_a = "'value'",
            trans_a = 'true',
            matrix_b =
                "'" + get_schema_testing() + ".matrix_sparse_100_100'",
            row_b = "'row_id'",
            col_b = "'col_b'",
            val_b = "'value'",
            trans_b = 'true',
            matrix_r = ['NULL', "''"]
        )
    )

    template = run_sql

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
