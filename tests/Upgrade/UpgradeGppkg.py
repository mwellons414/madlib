
from madlib.src.template.madlib_upgrade import MADlibUpgradeTestCase
import os

pwd = os.getcwd()

# ----------------------------------------------------------------------

class UpgradeTestCase_06_07_gppkg (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.6 to v0.7
    """
    load_dir = "test_0.6_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.6_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.6_0.7/ans"

    old_version = "0.6"
    old_pkg_type = "gppkg"
    old_download_link = None
    old_file_location = pwd + "/madlib/madlib-1.3-rhel5-x86_64.gppkg"
    new_version = "0.7"
    new_pkg_type = "gppkg"
    new_download_link = None
    new_file_location = pwd + "/madlib/madlib-1.4-rhel5-x86_64.gppkg"
    