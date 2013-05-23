
## ------------------------------------------------------------------------
## Mapping from version string to skip-list name
## ------------------------------------------------------------------------

import re
from madlib.src.test_utils.utils import biprint

# ------------------------------------------------------------------------

skip_map = {"greenplum" : {"4.2.5.0" : "skip_gp42",
                           "4.2.4.0" : "skip_gp42",
                           "4.2.3.0" : "skip_gp42",
                           "4.1.3.0" : "skip_gp41"},
            
            "postgres" : {"9.2.4" : "skip_pg92",
                          "9.2.3" : "skip_pg92",
                          "9.1.9" : "skip_pg91",
                          "9.0.13" : "skip_pg90"}}

# ------------------------------------------------------------------------

def version_skip_map (kind, version, mod):
    """
    Create the mapping from version to skip
    The version specific skip-list is the union of, for example,
    skip_all, skip_gp4, skip_gp42, skip_gp425
    """
    skip_head = "skip_gp" if kind == "greenplum" else "skip_pg" 
    m = re.search(r"^(\d+\.\d+\.\d+)", version)
    s = m.group(1).replace(".", "")
    skip_name = skip_head + s
    skip3 = get_skip(mod, skip_name)
    if len(skip3) > 0:
        biprint("-- skip-list '" + skip_name + "' is used.")
    
    m = re.search(r"^(\d+\.\d+)", version)
    s = m.group(1).replace(".", "")
    skip_name = skip_head + s
    skip2 = get_skip(mod, skip_name)
    if len(skip2) > 0:
        biprint("-- skip-list '" + skip_name + "' is used.")

    m = re.search(r"^(\d+)", version)
    s = m.group(1).replace(".", "")
    skip_name = skip_head + s
    skip1 = get_skip(mod, skip_name)
    if len(skip1) > 0:
        biprint("-- skip-list '" + skip_name + "' is used.")

    skip_name = skip_head
    skip0 = get_skip(mod, skip_name)
    if len(skip0) > 0:
        biprint("-- skip-list '" + skip_name + "' is used.")

    # all skip
    skip_a = get_skip(mod, "skip_all")
    if len(skip_a) > 0:
        biprint("-- skip-list 'skip_all' is used.")

    return skip_a + skip0 + skip1 + skip2 + skip3

# ------------------------------------------------------------------------

def get_skip (mod, skip_name):
    try:
        skip = getattr(mod, skip_name)
    except:
        skip = []
    return skip