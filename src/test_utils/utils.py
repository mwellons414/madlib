
"""
Some utilities
"""
from gppylib.commands.base import Command
from tinctest import logger
import re
import os
import sys
import time
import random
from tinctest.lib import Gpdiff

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
    tmp_r = "/tmp/" + unique_string()
    try:
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
                        if ms == "method.name_":
                            if "method.name_" in params.keys():
                                sys.exit("methodName is used for R output file names, and has duplicates in parameter list!")
                            value = methodName + ".sql"
                        elif ms == "ans.path_":
                            if "ans.path_" in params.keys():
                                sys.exit("ans_path is used for R output file path, and has duplicates in parameter list!")
                            value = ans_path
                        elif ms.startswith("_"):
                            ms = "`" + ms + "`"
                        else:
                            value = params[ms]
                    except:
                        sys.exit("The parameter of R script does not match with test case!")
                    tmpf.write(ms + " = \"" + str(value) + "\"\n")
                else:
                    tmpf.write(line + "\n")
        tmpf.close()
    except:
        os.system("rm -f " + tmp_r + " " + tmp_r + ".out")
        sys.exit("MADlib Test Error: cannot pass parameters to R script!")

    # execute the tmp R script
    os.system("R -q --no-save < " + tmp_r + " > " + tmp_r + ".out")
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

# ------------------------------------------------------------------------

def execute_cmd (name, cmdStr):
    """
    Execute a command with proper log info
    """
    logger.info(
        """
        ---------------------------- Run command -----------------------
        %s
        ----------------------------------------------------------------
        """ % cmdStr)
    cmd = Command(name = name, cmdStr = cmdStr)
    logger.info("\n" + name + "\n")
    cmd.run(validateAfter = False)
    res = cmd.get_results()
    logger.info(
        """
        ---------------------------- Output -----------------------
        %s
        -----------------------------------------------------------
        """ % res)
    return res

# ------------------------------------------------------------------------

def biprint (info, syswrite = False, sysexit = False):
    """
    Print to both logger and std
    """
    logger.info("================================================================\n")
    logger.info(info + "\n")
    logger.info("================================================================\n")
    if syswrite:
        sys.stdout.write(info)
        sys.stdout.flush()
    else:
        print(info)
        sys.stdout.flush()
    if sysexit:
        sys.exit()

# ------------------------------------------------------------------------

def modified_Gpdiff (result, answer):
    """
    Gpdiff cannot ignore the path name in lines with INFO
    but it can ignore the different path name in lines with ERROR
    """
    dirname = os.path.dirname(result)
    tmp_name = unique_string()
    res_tmp = dirname + "/" + tmp_name + ".sql.out"
    ans_tmp = dirname + "/" + tmp_name + ".ans"
    diff_tmp = dirname + "/" + tmp_name + ".sql.diff"
    diff_real = result.replace("sql.out", "sql.diff")

    r = open(res_tmp, "w")
    with open(result, "r") as f:
        for line in f:
            if line.startswith("Time"):
                # r.write("\n")
                next
            if re.search("INFO", line):
                r.write(line.replace("INFO", "ERROR"))
            else:
                r.write(line)
    r.close()

    s = open(ans_tmp, "w")
    with open(answer, "r") as f:
        for line in f:
            if line.startswith("Time"):
                # s.write("\n")
                next
            if re.search("INFO", line):
                s.write(line.replace("INFO", "ERROR"))
            else:
                s.write(line)
    s.close()

    cmr = Gpdiff.are_files_equal(res_tmp, ans_tmp)

    if os.path.exists(diff_tmp):
        os.system("mv " + diff_tmp + " " + diff_real)
    os.system("rm -rf " + res_tmp)
    os.system("rm -rf " + ans_tmp)

    return cmr

# -------------------------------------------------------------------------
def _get_argument_expansion(arg_dict, default_arg_val):
    """
    Generates a list of dictionaries, each dictionary corresponding to
    a specific value for one argument, with other arguments taking default values.

    This function is a helper function created to ease the input of various
    values for arguments. Following the example should make it easier to understand.

    Inputs:
        arg_dict = { arg1=[1, 2, 3],
                     arg2=[A, B, C],
                     arg3=[X, Y, Z]}
        default_arg_val = { arg1=A1,
                            arg2=A2,
                            arg3=A3}
    Output:
        [ {arg1=1, arg2=A2, arg3=A3}, {arg1=2, arg2=A2, arg3=A3}, {arg1=3, arg2=A2, arg3=A3},
          {arg1=A1, arg2=A, arg3=A3}, {arg1=A1, arg2=B, arg3=A3}, {arg1=A1, arg2=C, arg3=A3},
          {arg1=A1, arg2=A2, arg3=X}, {arg1=A1, arg2=A2, arg3=Y}, {arg1=A1, arg2=A2, arg3=Z},
        ]

    Number of dictionaries in the output list is the sum of all possible values
    taken by the arguments.

    Args:
        @param argument_dict Dictionary {argument_name: [values for argument]}
        @param default_arg_val Dictionary {argument_name: default_value}

    Returns:
        List of dictionaries, each dictionary with single value for each argument
        and default values for the other arguments
    """
    if not isinstance(arg_dict, dict):
        return arg_dict
    arg_dict_list = []  # output a list of argument dictionaries
    for each_arg_key, each_arg_vals in arg_dict.iteritems():
        for each_val in each_arg_vals:
            curr_arg_dict = dict((k,v) for k, v in default_arg_val.iteritems())
            # this is slower than a dictionary composition but TINC is not
            #  guaranteed to use Python 2.7 or higher
            curr_arg_dict[each_arg_key] = each_val
            arg_dict_list.append(curr_arg_dict)
    return arg_dict_list
# -------------------------------------------------------------------------
def relative_mean_squared_error (vec1, vec2):
    """
    Assume that the two vectors have the same length
    """
    if vec1 is None or vec2 is None:
        sys.exit("Utility Error: mean_squared_error: Empty vector")
    sum = 0.
    norm_vec1 = 0.
    N = len(vec1)
    try:
        for i in range(len(vec1)):
            sum += (vec1[i] - vec2[i])**2
            norm_vec1 += vec1[i]**2
    except:
        sys.exit("Utility Error: mean_squared_error: Type error for %s or %s" % (vec1,vec2))
    if norm_vec1 >= 1:
        return sum/(N * norm_vec1)
    else:
        return sum/N

# ------------------------------------------------------------------------
def parse_all_R_output(resultFile, params_dict, results_dict):
  """
  Read R results from the answer file.
  Read only once for all the tests
  """
  count = 0
  return_dict = dict()
  params_keys = sorted(params_dict.values())
  results_keys = sorted(results_dict.values())

  # Parse and cleanup 
  r_results = open(resultFile, 'r').readlines()
  r_results = map(lambda x: x.strip().lower(), r_results)
  
  # Number of lines in the r_results segment files
  block_size = 0
  for line in r_results:
    if not line.strip():
      block_size += 1
      break
    else:
      block_size += 1
      
  # Read all results and options datasetwise (blockwise)
  for i in range(0, len(r_results), block_size):
      block = r_results[i:i+block_size]
      options = map(lambda x: block[x], params_keys)
      results = {}
      for r in results_dict:
        results[r] = map(float, block[results_dict[r]].split(','))
      return_dict[tuple(options)] = results
    
  return return_dict

# ------------------------------------------------------------------------
def parse_single_SQL_output(result, result_dict):
    """
    Extract all the outputs
    """
    parsed_params = 0
    # Invert the python dictionary
    inv_result_dict = {}
    sorted_keys = sorted(result_dict.keys(), key=lambda x: result_dict[x])
    for i,k in enumerate(sorted_keys):
      inv_result_dict[i] = k
 
    return_dict = {}
    for line in result:
        if parsed_params in inv_result_dict:
          tag = inv_result_dict[parsed_params]
        pattern = ".*?\{(.*?)\}"
        s = re.match(tag + pattern, line)
        #s = re.match(r"^[^\{]*\{([^\}]*)\}", line)
        if s is not None:
            try:
                res = map(float, string_to_array(s.group(1)))
                return_dict[inv_result_dict[parsed_params]] = res 
                parsed_params += 1
            except:
                sys.exit("SQL parser error: Not float type for %s" % \
                                inv_result_dict[parsed_params])
            if res is None:
                sys.exit("SQL parser error: Empty array for %s" % parsed_params)
    return return_dict


