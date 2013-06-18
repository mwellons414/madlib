
# ------------------------------------------------------------------------
# Right now, TINC does not support skip different test cases for different
# versions of GPDB.
#
# So, as a temporary workaround, we keep a record of skipped test cases here.
# Environment variable SKIP can control which skip sets to use.
#
# Usage:
#
# SKIP=outskip tinc.py tests.cox_proportional_hazards.CoxPropHazardsOutputTest
#
#
# We can define a universal skip set name for a specific version of GPDB
# across all test cases, and when we use it, only certain
# ------------------------------------------------------------------------

outskip = []
inskip = []

# ------------------------------------------------------------------------
# We can use the following convention
# If we use these names in all skip files in different folders,
# We can just skip these tests by setting, for example,
# SKIP=skip_gp41

# Skip these tests for all versions of GPDB & PG
skip_all = []

# Skip these tests only for GPDB4.1.2
skip_gp41 = []

# skip these tests only for PG9.0
skip_pg90 = []

skip_pg92 = inskip
