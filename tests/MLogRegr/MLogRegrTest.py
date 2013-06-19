
## MADlib Tests for linear regression
## For learning tinc

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import string_to_array
from madlib.src.test_utils.utils import mean_squared_error
from madlib.src.test_utils.utils import read_sql_result
from madlib.src.test_utils.get_dbsettings import get_schema_testing
import os
import re
import sys

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MlogregrOutputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;
        select * from {schema_madlib}.mlogregr(
            '{schema_testing}.{dataset}',
            '{depvar}', 
            '{indepvar}', 
            20,
            'irls',
            0.0001,
            0);
        """
    ans_dir = "expected_output"
    template_method = "mlogregr%{dataset}"
    template_doc = "This is for output tests of multinomial logistic regression."

    template_vars = dict(
        dataset = ['mlogr_recordlink', 'mlogr_pokerhand'],
        depvar = 'y',
        indepvar = 'x')

    template = run_sql
    MADlibTestCase.db_settings_["psql_options"] = "-x"

    def read_file(self, filename):
        for line in open(filename).readlines():
            if line.startswith('coef'):
                content = line.split('|')[1].strip()
                content = content.replace('{', '').replace('}', '')
                return eval(content)

    def validate (self, sql_resultfile, r_answerfile):
        answer = self.read_file(r_answerfile)
        result = self.read_file(sql_resultfile)
        if sql_resultfile.find('mlogr_pokerhand') > 0:
            return mean_squared_error(result, answer) < 1e1
        else:
            return mean_squared_error(result, answer) < 1e-2

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class MlogregrInputTestCase (MADlibTestCase):
    """
    Run templated SQL tests
    """
    run_sql = """
        set client_min_messages to error;
        select * from {schema_madlib}.mlogregr(
            {dataset},
            {depvar}, 
            {indepvar}, 
            {maxnumiterations},
            {optimizer}, 
            {precision},
            {ref_category});
        """

    ans_dir = "expected_input" if MADlibTestCase.dbKind() == "greenplum" else "expect_input_pg"
    template_method = "mlogregr{incr_}"
    template_doc = "This is for input tests of multinomial logistic regression."

    template_vars = []
    template_vars.append(
        dict(
            dataset = ["NULL", "''", "'non_existing_input_table'"],
            depvar = "'y'",
            indepvar = "'x'",
            maxnumiterations = 20,
            optimizer = "'irls'",
            precision = 0.0001,
            ref_category = 0
        )
    )
    template_vars.append(
        dict(
            dataset = "'" + get_schema_testing() + ".mlogr_pokerhand'",
            depvar = ["NULL", "''", "'non_exisiting_depvar'"],
            indepvar = "'x'",
            maxnumiterations = 20,
            optimizer = "'irls'",
            precision = 0.0001,
            ref_category = 0
        )
    )
    template_vars.append(
        dict(
            dataset = "'" + get_schema_testing() + ".mlogr_pokerhand'",
            depvar = "'y'",
            indepvar = ["NULL", "''", "'non_exisiting_indepvar'"],
            maxnumiterations = 20,
            optimizer = "'irls'",
            precision = 0.0001,
            ref_category = 0
        )
    )
    template_vars.append(
        dict(
            dataset = "'" + get_schema_testing() + ".mlogr_pokerhand'",
            depvar = "'y'",
            indepvar = "'x'",
            maxnumiterations = [-1, 0, 'NULL'],
            optimizer = "'irls'",
            precision = 0.0001,
            ref_category = 0
        )
    )
    template_vars.append(
        dict(
            dataset = "'" + get_schema_testing() + ".mlogr_pokerhand'",
            depvar = "'y'",
            indepvar = "'x'",
            maxnumiterations = 20,
            optimizer = ["NULL", "''", "'non_exisiting_optimizer'"],
            precision = 0.0001,
            ref_category = 0
        )
    )
    template_vars.append(
        dict(
            dataset = "'" + get_schema_testing() + ".mlogr_pokerhand'",
            depvar = "'y'",
            indepvar = "'x'",
            maxnumiterations = 20,
            optimizer = "'irls'",
            precision = 'NULL',
            ref_category = 0
        )
    )
    template_vars.append(
        dict(
            dataset = "'" + get_schema_testing() + ".mlogr_pokerhand'",
            depvar = "'y'",
            indepvar = "'x'",
            maxnumiterations = 20,
            optimizer = "'irls'",
            precision = 0.0001,
            ref_category = [-1, 100, 'NULL']
        )
    )

    template = run_sql
