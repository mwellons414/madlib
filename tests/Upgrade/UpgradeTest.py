from madlib.src.template.madlib_upgrade import MADlibUpgradeTestCase

# ------------------------------------------------------------------------

class UpgradeTestCase_06_07 (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.6 to v0.7
    """
    load_dir = "test_0.6_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.6_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.6_0.7/ans" 
    out_dir = "test_0.6_0.7/result"
    
    old_version = "0.6" 
    old_pkg_type = "source"
    old_download_link = None
    old_file_location = "~/Downloads/madlib-v0.6.tar.gz"
    new_version = "0.7"
    new_pkg_type = "source"
    new_download_link = None 
    new_file_location = "~/Downloads/madlib-v0.7.tar.gz"

    schema_madlib = "upgrade_madlib" 
    upgrade_dir = "upgrade_home" 

# ------------------------------------------------------------------------

class UpgradeTestCase_05_07 (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.5 to v0.7
    """
    load_dir = "test_0.5_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.5_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.5_0.7/ans" 
    out_dir = "test_0.5_0.7/result"

    old_version = "0.5" 
    old_pkg_type = "source"
    old_download_link = None
    old_file_location = "~/Downloads/madlib-v0.5.tar.gz"
    new_version = "0.7"
    new_pkg_type = "source"
    new_download_link = None 
    new_file_location = "~/Downloads/madlib-v0.7.tar.gz"

    schema_madlib = "upgrade_madlib" 
    upgrade_dir = "upgrade_home" 

