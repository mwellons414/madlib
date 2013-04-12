
# ------------------------------------------------------------------------
# Right now, TINC does not support skip different test cases for different
# versions of GPDB.
#
# So, as a temporary workaround, we keep a record of skipped test cases here.
# Environment variable SKIP can control which skip sets to use.
#
# Usage:
#
# SKIP=outskip tinc.py examples.linregr_test.LinregrOutputTesCase
#
# or
#
# SKIP=examples.linregr_skip.outskip tinc.py examples.linregr_test.LinregrOutputTesCase
#
# We can define a universal skip set name for a specific version of GPDB
# across all test cases, and when we use it, only certain
# ------------------------------------------------------------------------

outskip = [{"dataset":"lin_auto_mpg_oi"},
          {"dataset":"lin_auto_mpg_wi", "hetero":"FALSE"}]

inskip = [{"dataset":"lin_auto_mpg_wi", "hetero":"FALSE"}]

# ------------------------------------------------------------------------
# We can use the following convention
# If we use these names in all skip files in different folders,
# We can just skip these tests by setting, for example,
# SKIP=skip_gp41

# Skip these tests for all versions of GPDB & PG
skip_all = []

# Skip these tests only for GPDB4.1.2
skip_gp412 = skip_all + []

# skip these tests only for PG9.0
skip_pg90 = skip_all + []