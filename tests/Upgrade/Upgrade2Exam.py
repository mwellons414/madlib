
from madlib.src.template.madlib_upgrade import MADlibUpgradeTestCase
import os

pwd = os.getcwd()

# ------------------------------------------------------------------------

class UpgradeTestCase_05_07_gppkg (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.5 to v0.7
    """
    load_dir = "test_0.5_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.5_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.5_0.7/ans"

    old_version = "0.5"
    old_pkg_type = "gppkg"
    old_download_link = None
    old_file_location = pwd + "/madlib/madlib-1.2-rhel5-x86_64.gppkg"
    new_version = "0.7"
    new_pkg_type = "gppkg"
    new_download_link = None
    new_file_location = pwd + "/madlib/madlib-1.4-rhel5-x86_64.gppkg"

# ------------------------------------------------------------------------

class UpgradeTestCluster_06_07_rpm (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.6 to v0.7
    """
    load_dir = "test_0.6_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.6_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.6_0.7/ans"

    old_version = "0.6"
    old_pkg_type = "rpm"
    old_download_link = None
    old_file_location = pwd + "/madlib/madlib-0.6-Linux.rpm"
    new_version = "0.7"
    new_pkg_type = "rpm"
    new_download_link = None
    new_file_location = pwd + "/madlib/madlib-0.7-Linux.rpm"

    hosts_file = "/data/hai/hosts"

# ------------------------------------------------------------------------

class UpgradeTestCluster_05_07_rpm (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.5 to v0.7
    """
    load_dir = "test_0.5_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.5_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.5_0.7/ans"

    old_version = "0.5"
    old_pkg_type = "rpm"
    old_download_link = None
    old_file_location = pwd + "/madlib/madlib-0.5-Linux.rpm"
    new_version = "0.7"
    new_pkg_type = "rpm"
    new_download_link = None
    new_file_location = pwd + "/madlib/madlib-0.7-Linux.rpm"

    hosts_file = "/data/hai/hosts"

# ------------------------------------------------------------------------

class UpgradeTestCluster_06_07_src (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.6 to v0.7
    """
    eigen_pkg = "/data/hai/3.1.2.tar.gz"
    load_dir = "test_0.6_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.6_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.6_0.7/ans"

    old_version = "0.6"
    old_pkg_type = "source"
    old_download_link = None
    old_file_location = pwd + "/madlib/madlib-v0.6.tar.gz"
    new_version = "0.7"
    new_pkg_type = "source"
    new_download_link = None
    new_file_location = pwd + "/madlib/madlib-v0.7.tar.gz"

    hosts_file = "/data/home/gpdbchina/422build6/data/cQA24/hosts"

# ------------------------------------------------------------------------

class UpgradeTestCluster_05_07_src (MADlibUpgradeTestCase):
    """
    Tests for upgrading MADlib from v0.5 to v0.7
    """
    eigen_pkg = "/data/hai/3.1.2.tar.gz"
    load_dir = "test_0.5_0.7/sql"
    load_prefix = "create_"
    sql_dir = "test_0.5_0.7/sql"
    sql_prefix = "check_"
    ans_dir = "test_0.5_0.7/ans"

    old_version = "0.5"
    old_pkg_type = "source"
    old_download_link = None
    old_file_location = pwd + "/madlib/madlib-v0.5.tar.gz"
    new_version = "0.7"
    new_pkg_type = "source"
    new_download_link = None
    new_file_location = pwd + "/madlib/madlib-v0.7.tar.gz"

    hosts_file = "/data/home/gpdbchina/422build6/data/cQA24/hosts"

