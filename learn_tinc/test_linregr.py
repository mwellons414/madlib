'''
Madlib tests
'''

from tinctest.models.gpdb.sql    import SQLTestCase
from tinctest.models.gpdb.madlib import MADlibTemplateTestCase

'''
class MADlibSQLTestCase(SQLTestCase):
    """
    Runs the .sql scripts in the current directory
    """
    sql_dir='sql'
    ans_dir='sql'
'''

linregr_sql = """
SELECT (linregr).coef
FROM (SELECT {madlib_schema}.linregr(y,x)
      FROM (values (1,array[1,2]), (2,array[1,3])) as {dataset}(y, x)
 ) as q;
"""

linregr_R = """
m = lm(y~x, data = data.frame(y=c(1,2),x=c(2,3)));
as.vector(coef(m))
"""


class LinearRegressionTestCase(MADlibTemplateTestCase):
    """
    Runs templated SQL tests
    """
    sql_dir='result'
    out_dir='result'
    ans_dir='ans'

    # Required by superclass
    template_method = "linregr_{dataset}"
    template_doc = ""
    template_vars = {
        'madlib_schema':  'madlib',
        'test_schema':    'madlibtestdata',
        'dataset':       ['a','b']
        }

    template   = linregr_sql
    template_R = linregr_R

    def validate(self, sql_resultfile, R_resultfile, answerfile):
        """ 
        Examine the two output files and determine if they are equivalent 

        At the moment this is very specific and tailored to this one example, it may
        be benificial to improve the overall result handling.
        """
        with open(sql_resultfile, 'r') as f:
            for line in f:
                # Look a line that looks like '^ {...}$'
                if line.startswith(' {') and line.endswith('}\n'):
                    sql_result = line[2:-2]

        with open(R_resultfile, 'r') as f:
            for line in f:
                if line.startswith('[1]') and line.endswith('\n'):
                    r_result = ','.join(line[3:-1].split())

        self.assertEqual(sql_result, r_result)
        return sql_result == r_result






"""
    template_vars = {
        'madlib_schema':  'madlib',
        'test_schema':    'madlibtestdata',
        'dataset': ['lin_Concrete_oi',
                    'lin_Concrete_wi',
                    'lin_auto_mpg_oi',
                    'lin_auto_mpg_wi',
                    'lin_communities_unnormalized_oi',
                    'lin_communities_unnormalized_wi',
                    'lin_communities_oi',
                    'lin_communities_wi',
                    'lin_flare_oi',
                    'lin_flare_wi',
                    'lin_forestfires_oi',
                    'lin_forestfires_wi',
                    'lin_housing_oi',
                    'lin_housing_wi',
                    'lin_imports_85_oi',
                    'lin_imports_85_wi',
                    'lin_machine_oi',
                    'lin_machine_wi',
                    'lin_noobservation_oi',
                    'lin_noobservation_wi',
                    'lin_o_ring_erosion_only_oi',
                    'lin_o_ring_erosion_only_wi',
                    'lin_o_ring_erosion_or_blowby_oi',
                    'lin_o_ring_erosion_or_blowby_wi',
                    'lin_parkinsons_updrs_oi',
                    'lin_parkinsons_updrs_wi',
                    'lin_redundantobservations_oi',
                    'lin_redundantobservations_wi',
                    'lin_servo_oi',
                    'lin_servo_wi',
                    'lin_singleobservation_oi',
                    'lin_singleobservation_wi',
                    'lin_slump_oi',
                    'lin_slump_wi',
                    'lin_winequality_red_oi',
                    'lin_winequality_red_wi',
                    'lin_winequality_white_oi',
                    'lin_winequality_white_wi'],
        }
"""



