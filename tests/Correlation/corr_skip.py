from madlib.src.test_utils.get_dbsettings import get_schema_testing

def skip_some ():
    schema_testing = get_schema_testing()
    dataset = [
        "'" + schema_testing + ".dt_golf'",
        "'" + schema_testing + ".non_exists_table'",
        "NULL", "''"]
    tbl_output = [
        "__madlib_temp_40418089_1365619947_6556506__", 
        "NULL", "''"]
    target_cols = [
        "'non_exists_cols'", 
        "'windy, outlook'", 
        "'humidity, temperature'", 
        "NULL", "''"]

    skip = []
    for data in dataset:
        for output in tbl_output:
            if output != "__madlib_temp_40418089_1365619947_6556506__":
                for target in target_cols:
                    if data == "'" + schema_testing + ".dt_golf'" and target == "NULL":
                        continue
                    else:
                        skip.append(dict(dataset=data, tbl_output=output, 
                            target_cols=target))
    return skip

inskip = skip_some()

# ------------------------------------------------------------------------
# We can use the following convention
# If we use these names in all skip files in different folders,
# We can just skip these tests by setting, for example,
# SKIP=skip_gp41

# Skip these tests for all versions of GPDB & PG
skip_all = inskip

# Skip these tests only for GPDB4.1.2
skip_gp41 = []

# skip these tests only for PG9.0
skip_pg90 = []
