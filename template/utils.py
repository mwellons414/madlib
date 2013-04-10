
"""
Some utilities
"""

import re
import time
import random

def unique_string ():
    """
    Generate random remporary names for temp table and other names.
    """
    r1 = random.randint(1, 100000000)
    r2 = int(time.time())
    r3 = int(time.time()) % random.randint(1, 100000000)
    u_string = "__madlib_temp_" + str(r1) + "_" + str(r2) + "_" + str(r3) + "__"
    return u_string

## ========================================================================

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
    for m in re.finditer(r"(\"(\\\"|[^\"])*\"|[^\",\s]+)", s):
        elm.append(m.group(1))
    for i in range(len(elm)):
        elm[i] = elm[i].strip()
    return elm

## ========================================================================

def mean_squared_error (vec1, vec2):
    """
    Assume that the two vectors have the same length
    """
    sum = 0.
    for i in range(len(vec1)):
        sum += (vec1[i] - vec2[i])**2
    return sum / float(len(vec1))