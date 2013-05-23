
from madlib.src.template.madlib_upgrade import MADlibUpgradeTestCase
import os

pwd = os.getcwd()

# ------------------------------------------------------------------------

class UpgradeTestCase_06_07_dmg (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.6 to v0.7
    """
    load_dir = "test_0.6_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.6_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.6_0.7/ans" 
    
    old_version = "0.6" 
    old_pkg_type = "dmg"
    old_download_link = None
    old_file_location = "/Users/qianh1/Downloads/dmg/madlib-0.6-Darwin.dmg"
    new_version = "0.7"
    new_pkg_type = "dmg"
    new_download_link = None 
    new_file_location = "/Users/qianh1/Downloads/dmg/madlib-0.7-Darwin.dmg"

# ------------------------------------------------------------------------

class UpgradeTestCase_05_07_dmg (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.5 to v0.7
    """
    load_dir = "test_0.5_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.5_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.5_0.7/ans" 

    old_version = "0.5" 
    old_pkg_type = "dmg"
    old_download_link = None
    old_file_location = "/Users/qianh1/Downloads/dmg/madlib-0.5-Darwin.dmg"
    new_version = "0.7"
    new_pkg_type = "dmg"
    new_download_link = None 
    new_file_location = "/Users/qianh1/Downloads/dmg/madlib-0.7-Darwin.dmg"