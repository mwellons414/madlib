
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

inskip = [{"dataset":"lin_auto_mpg_wi", "hetero":"TRUE"}]

# --------------------------------

def skip_some ():
    """
    Use a small function to generate skip list
    """
    datasets = ["lin_auto_mpg_oi", "lin_auto_mpg_wi", "lin_fdic_clean"]
    skip = []
    for data in datasets:
        if data != "lin_auto_mpg_oi":
            skip.append(dict(dataset = data, hetero = "FALSE"))
    return skip

skip2 = skip_some()

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
