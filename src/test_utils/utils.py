
"""
Some utilities
"""

import re
import os
import sys
import time         
import random

# ------------------------------------------------------------------------

def call_R_script (script, ans_path, methodName, params):
    """
    call external R script using the paprams
    First, replace the parameter values in R
    Second, execute R script

    Thus, this requires that the R script must start
    with parameter definition like
    ## @madlib-param dataset
    """
    tmp_r = "tmp/" + unique_string()
    tmpf = open(tmp_r, "w")
    with open(script, "r") as f:
        for line in f:
            line = line.strip("\n")
            h = re.match("^\s*##\s*@madlib-param\s+", line)
            if h is not None:
                s = re.match(r"^\s*##\s*@madlib-param\s+(\S*)\s*",
                             line)
                try:
                    ms = s.group(1)
                    if ms == "methodName":
                        if "methodName" in params.keys():
                            sys.exit("methodName is used for R output file names, and has duplicates in parameter list!")
                        value = methodName + ".sql"
                    elif ms == "ans_path":
                        if "ans_path" in params.keys():
                            sys.exit("ans_path is used for R output file path, and has duplicates in parameter list!")
                        value = ans_path
                    else:
                        value = params[ms]
                except:
                    sys.exit("The parameter of R script does not match with test case!")
                tmpf.write(ms + " = \"" + value + "\"\n")
            else:
                tmpf.write(line + "\n")
    tmpf.close()

    # execute the tmp R script
    os.system("R --no-save < " + tmp_r + " > " + tmp_r + ".out")
    os.system("rm -f " + tmp_r + " " + tmp_r + ".out")
    
# ------------------------------------------------------------------------

def read_record (f):
    """
    Read in records separated by an empty line
    usually in R result file
    To be implemented
    """
    pass

# ------------------------------------------------------------------------
    
def read_sql_result (resultfile):
    """
    Read the result file into a dictionary,
    which has two elements: madlib_params & result.
    "madlib_params" stores all parameters
    "result" stores the actual output
    """
    res = dict(madlib_params = dict(),
               result = [])
    with open(resultfile, "r") as f:
        for line in f:
            line = line.strip("\n")
            h = re.match("^\s*--\s*@madlib-param\s+", line)
            if h is not None:
                s = re.match(r"^\s*--\s*@madlib-param\s+(.*)$",
                             line).group(1)
                m = re.match(r"(\S+)\s*=\s*\"(.*)\"\s*$", s)
                res["madlib_params"][m.group(1)] = m.group(2)
            else:
                res["result"].append(line)
    return res
            
# ------------------------------------------------------------------------

def unique_string ():
    """
    Generate random temporary names for temp table and other names.
    """
    r1 = random.randint(1, 100000000)
    r2 = int(time.time())
    r3 = int(time.time()) % random.randint(1, 100000000)
    u_string = "__madlib_temp_" + str(r1) + "_" + str(r2) + "_" + str(r3) + "__"
    return u_string

# ------------------------------------------------------------------------

def string_to_array (s):
    """
    Split a string into an array of strings
    Any space around the substrings are removed

    Requirement: every individual element in the string
    must be a valid Postgres name, which means that if
    there are spaces or commas in the element then the
    whole element must be quoted by a pair of double
    quotes.

    Usually this is not a problem. Especially in older
    versions of GPDB, when an array is passed from
    SQL to Python, it is converted to a string, which
    automatically adds double quotes if there are spaces or
    commas in the element.

    So use this function, if you are sure that all elements
    are valid Postgres names.
    """
    elm = []
    try:
        for m in re.finditer(r"(\"(\\\"|[^\"])*\"|[^\",\s]+)", s):
            elm.append(m.group(1))
        for i in range(len(elm)):
            elm[i] = elm[i].strip()
    except:
        sys.exit("Utility Error: string_to_array - cannot convert!")
    return elm

# ------------------------------------------------------------------------

def mean_squared_error (vec1, vec2):
    """
    Assume that the two vectors have the same length
    """
    if vec1 is None or vec2 is None:
        sys.exit("Utility Error: mean_squared_error - vector is None!")
    sum = 0.
    try:
        for i in range(len(vec1)):
            sum += (vec1[i] - vec2[i])**2
    except:
        sys.exit("Utility Error: mean_squared_error - cannot comput!")
    return sum / float(len(vec1))



