
# ------------------------------------------------------------------------
# Test upgrade example
# ------------------------------------------------------------------------

from madlib.src.template.madlib_upgrade import MADlibUpgradeTestCase

# ------------------------------------------------------------------------

class ExampleUpgradeTestCase (MADlibUpgradeTestCase):
    """
    An example of MADlib upgrade test case
    """
    # create the testing data structure
    load_dir = "test_0.6_0.7"
    load_prefix = "create_"

    # actual test case
    sql_dir = "test_0.6_0.7"
    sql_prefix = "check_"

    ans_dir = "test_0.6_0.7" # answer folder

    # odler version info
    # must specify either one of file_location and download_link
    old_version = "0.6" 
    old_pkg_type = "source"
    old_download_link = None
    old_file_location = "~/Downloads/madlib-v0.6.tar.gz"

    # newer version info
    # must specify either one of file_location and download_link
    new_version = "0.7"
    new_pkg_type = "source"
    new_download_link = None 
    new_file_location = "~/Downloads/madlib-v0.7.tar.gz"
    