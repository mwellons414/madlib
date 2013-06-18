
# ------------------------------------------------------------------------
# Upgrade test for MADlib
# ------------------------------------------------------------------------

from madlib.src.template.gpmad import gpmad
from madlib.src.template.sql import MADlibSQLTestCase
from madlib.src.template.lib import PSQL1
from madlib.src.test_utils.get_dbsettings import get_dbsettings
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import execute_cmd
from madlib.src.test_utils.utils import biprint
from madlib.src.test_utils.get_dbsettings import get_db_name
from madlib.src.template.class_utils import make_sure_path_exists
from madlib.src.template.class_utils import get_env_flag
from madlib.src.template.class_utils import get_skip
from tinctest.lib import Gpdiff
import tinctest
from tinctest import logger
from gppylib.db import dbconn
# from gppylib.commands.base import Command
import urllib
import shutil
import os
import re
import sys
import time

# ------------------------------------------------------------------------

# MADlibTestCase cannot use this to get the db info
# because superuser is not needed to run MADlibTestCase
# and therefore may not be given by the user
def get_dbInfo ():
    """
    get the dbms kind and version
    """
    db_tmp = unique_string()
    try:
        execute_cmd(name = "Create temp database to get kind and version",
                    cmdStr = "dropdb " + db_tmp + "; createdb " + db_tmp)
        db = get_dbsettings("Identify db kind and version", db_tmp)
        execute_cmd(name = "Drop the temp database",
                    cmdStr = "dropdb " + db_tmp)
    except:
        sys.exit("************* Could not find kind and version of DBMS ***********")
    return (db["kind"], db["version"])
        
# ------------------------------------------------------------------------

class MADlibUpgradeTestCase (MADlibSQLTestCase):
    """
    Base class for an upgrade test case
    """
    eigen_pkg = None # if you cannot download eigen package
    
    load_dir = "load" # create testing data structure
    load_prefix = "" # load files start with this string

    sql_dir = "sql" # test case folder
    # sql_dir_tmp = unique_string() 
    sql_prefix = "" # test cases start with this string
    ans_dir = "expected"
    out_dir_head = "result_"
    
    hosts_file = None
    allowed_pkg_type = ["source", "rpm", "gppkg", "dmg"]

    old_version = None
    old_pkg_type = "source"
    old_download_link = None # need to download?
    old_file_location = None # alread in file system, just copy
    old_target_dir = None
    new_version = None
    new_pkg_type = "source"
    new_download_link = None
    new_file_location = None
    new_target_dir = None
    
    skip_file = None
    db_settings_ = None # get_dbsettings("MADlibUpgradeTestCase")
    
    # can control from environment variable
    schema_upgrade = "upgrade_madlib"
    # db_upgrade = unique_string()
    skip = []
    create_ans_ = False

    # upgrade_dir = unique_string() # "upgrade_home"

    # the current working dir
    working_dir = os.path.realpath(".")

    test_count = 0

    rpmdb_exists = False # Does RPM db already exist?

    # versions that do not support upgrade
    older_versions = ["0.5", "0.6"]

    cleanup = True # clean all intermediate folders

    already_tearDown = False

    dmg_install_dir = "/usr/local/madlib"

    cwd = os.getcwd() # current working dir

    dbInfo = get_dbInfo() # just get the kind and version of dbms

    # ----------------------------------------------------------------

    @classmethod
    def dbKind (cls):
        """
        greenplum or postgres
        """
        return cls.dbInfo[0]

    # ----------------------------------------------------------------
        
    @classmethod
    def dbVers (cls):
        """
        get the version number
        """
        m = re.search(r"^(\d+\.\d+\.\d+)", cls.dbInfo[1])
        return m.group(1)
    
    # ----------------------------------------------------------------

    @classmethod
    def _get_pkg_type (cls):
        """
        Get the package type
        """
        if os.environ.has_key("PKG_TYPE"):
            value = os.environ.get("PKG_TYPE")
            cls.old_pkg_type = value
            cls.new_pkg_type = value

        if ((cls.old_pkg_type not in cls.allowed_pkg_type) or
            (cls.new_pkg_type not in cls.allowed_pkg_type)):
            biprint("****** MADlib upgrade error: package type is not supported! ******")
            biprint("****** package type must be source, rpm or gppkg! ******", sysexit = True)

    # ----------------------------------------------------------------

    # For which version, the answers will be created
    @classmethod
    def _get_ans_version (cls):
        """
        get the version number that will be used to generate
        answer files
        """
        if os.environ.has_key("CREATE_ANS"):
            value = os.environ.get("CREATE_ANS")
            if value != cls.old_version and value != cls.new_version:
                biprint("****** MADlib upgrade test error: " +
                        cls.__module__ + "." + cls.__name__ +
                        " can only create answers for versions of " +
                        cls.old_version + " and " + cls.new_version
                        + " ******", sysexit = True)
            return value
        else:
            return False

    # ---------------------------------------------------------------- 

    # some utilities
    @classmethod
    def _get_upgrade_home (cls):
        """
        Get the target dir from the environment
        """
        if os.environ.has_key("UPHOME"):
            value = os.environ.get("UPHOME")
            if os.path.exists("./" + value):
                return os.path.realpath("./" + value)
            elif os.path.exists(value):
                return os.path.realpath(value)
        else:
            value = cls.upgrade_dir
            
        # cls_path = os.path.dirname(os.path.realpath(sys.modules[cls.__module__].__file__))
        # target = os.path.join(cls_path, value)
        target = os.path.join("/tmp", value) # create folder in /tmp
        if os.path.exists(target):
            return target
        else:
            try:
                execute_cmd(name = "mkdir target ...",
                            cmdStr = "mkdir {target}".format(target = target))
                return target
            except:
                biprint("****** MADlib Upgrade Error: no such directory for installing MADlib! ******",
                        sysexit = True)

            
    # ----------------------------------------------------------------

    # download MADlib package and install it on /usr/local/madlib
    @classmethod
    def _install_MADlib(cls, version, target_dir, pkg_type,
                        download_link = None,
                        file_location = None, msg = None):
        t0 = time.time()
        execute_cmd("Run command ...", "mkdir -p " + target_dir)
        logger.info("Starting the install for new MADlib ...")
        logger.info("----------------------------------------")
        if file_location is None:
            if pkg_type == "rpm" or pkg_type == "gppkg" or pkg_type == "dmg":
                install_file = cls._download_binary(version, target_dir,
                                                    download_link, msg)
                # check_md5sum (install_file, version)
            elif pkg_type == "source":
                install_file = cls._download_source(version, target_dir,
                                                    download_link, msg)
                # check_md5sum (install_file, version)
            else:
                cls.tearDown(True)
                biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
                biprint("****** MADlib Upgrade Error: no such package type (only 'rpm', 'gppkg' and 'source')! ******",
                        sysexit = True)
        else:
            if target_dir != os.path.realpath(os.path.dirname(file_location)):
                try:
                    execute_cmd("Run command ...", "cp " + file_location + " " + target_dir)
                    install_file = os.path.join(target_dir,
                                                os.path.basename(file_location))
                except:
                    cls.tearDown(True)
                    biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
                    biprint(file_location + " does not exist!", sysexit = True)
            else:
                install_file = file_location
                
        res = cls._unzip_download_and_install(version, install_file, pkg_type, target_dir, msg)

        t1 = time.time()

        biprint(msg + "%.2f ms ... ok\n" % (int((t1 - t0) * 100000)/100.), syswrite = True)

        return res

    # ----------------------------------------------------------------

    # uncompress MADlib package and install at /usr/local/madlib
    @classmethod
    def _unzip_download_and_install (cls, version, install_file, pkg_type, target_dir, msg):
        target_dir = os.path.dirname(install_file)
        if pkg_type == "source":
            logger.info("Untar source package ...")
            try:
                os.chdir(target_dir)
                execute_cmd("Run command ...", "rm -rf madlib; mkdir madlib; tar zxf " + 
                            install_file + " -C madlib")
                os.chdir("madlib")
                while "CMakeLists.txt" not in os.listdir("."):
                    dir_name = os.listdir(".")[0]
                    os.chdir(dir_name)

                install_dir = cls.upgrade_dir + "/local"
                execute_cmd("Run command ...", "mkdir -p " + install_dir)
                execute_cmd(name = "Build MADlib ...",
                            cmdStr = "./configure -DCMAKE_INSTALL_PREFIX="
                            + install_dir + "/madlib")

                if cls.eigen_pkg is not None:
                    execute_cmd("Run command ...", "cp " + cls.eigen_pkg + " build/third_party/downloads/")
                execute_cmd(name = "Continue building ...",
                            cmdStr = "cd build; make; make install")
                
                install_dir += "/madlib"
                os.chdir(cls.working_dir)
            except:
                cls.tearDown(True)
                biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
                biprint("****** MADlib Upgrade Error: cannot uncompress the tar.gz source package! ******",
                        sysexit = True)
        elif pkg_type == "rpm":
            if not cls.rpmdb_exists:
                logger.info("Initialize the local RPM database ...")
                execute_cmd("Run command ...", "mkdir -p " + cls.upgrade_dir + "/local/lib/rpm")
                if cls.hosts_file is not None:
                    execute_cmd(name = "Initialize local RPM database on hosts ...",
                                cmdStr =
                                """
                                gpssh -f {hosts_file} <<EOF
                                    mkdir -p {upgrade_dir}/local/lib/rpm;
                                EOF
                                """.format(upgrade_dir = cls.upgrade_dir,
                                           hosts_file = cls.hosts_file))
                execute_cmd(name = "Initialize local RPM database on master ...",
                            cmdStr = "rpm --initdb --root " + cls.upgrade_dir
                            + "/local --dbpath lib/rpm")
                if cls.hosts_file is not None:
                    execute_cmd(name = "Initialize local RPM database on hosts ...",
                                cmdStr =
                                """
                                gpssh -f {hosts_file} <<EOF
                                    rpm --initdb --root {upgrade_dir}/local --dbpath lib/rpm;
                                EOF
                                """.format(upgrade_dir = cls.upgrade_dir,
                                           hosts_file = cls.hosts_file))
                cls.rpmdb_exists = True
                
            logger.info("Installing RPM package ...")
            if version[0:3] in cls.older_versions:
                extra_prefix = "madlib/ "
            else:
                extra_prefix = " "
            try:
                os.chdir(target_dir)
                execute_cmd(name = "Installing RPM package on master...",
                            cmdStr = "rpm --root " + cls.upgrade_dir +
                            "/local --dbpath lib/rpm -i --nodeps --prefix=" + cls.upgrade_dir +
                            "/local/" + extra_prefix + install_file)
                
                if cls.hosts_file is not None: # may need to install on hosts
                    execute_cmd(name = "Create fodler on hosts ...",
                                cmdStr =
                                """
                                gpssh -f {hosts_file} <<EOF
                                    mkdir -p {target_dir};
                                EOF                                
                                """.format(hosts_file = cls.hosts_file,
                                           target_dir = target_dir))
                    execute_cmd(name = "Scp RPM package to hosts ...",
                                cmdStr =
                                """
                                gpscp -f {hosts_file} {install_file} '=:{target_dir}'
                                """.format(hosts_file = cls.hosts_file,
                                           install_file = install_file,
                                           target_dir = target_dir))
                    execute_cmd(name = "Installing RPM package on hosts ...",
                                cmdStr =
                                """
                                gpssh -f {hosts_file} <<EOF
                                    rpm --root {upgrade_dir}/local --dbpath lib/rpm -i --nodeps --prefix={upgrade_dir}/local/{extra_prefix}{install_file}
                                EOF
                                """.format(upgrade_dir = cls.upgrade_dir,
                                           hosts_file = cls.hosts_file,
                                           extra_prefix = extra_prefix,
                                           install_file = install_file))
                    
                install_dir = os.path.join(cls.upgrade_dir, "local/madlib")
            except:
                cls.tearDown(True)
                biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
                biprint("****** MADlib Upgrade Error: cannot install the .rpm binary packages! ******",
                        sysexit = True)
        elif pkg_type == "gppkg":
            gphome = os.environ.get("GPHOME")
            if version[0:3] in cls.older_versions:
                install_dir = gphome
            else:
                install_dir = gphome + "/madlib"
            execute_cmd(name = "Installing gppkg package ...",
                        cmdStr = "gppkg -i " + install_file)
        elif pkg_type == "dmg":
            try:
                res = execute_cmd(name = "Mounting DMG image ...",
                                  cmdStr = "hdiutil mount " + install_file)
            except:
                biprint("****** MADlib upgrade error: could not mount the dmg image! ******",
                        sysexit = True)
                
            m = re.search("(/Volumes/[^\n]*)\n", str(res))
            if m is None:
                biprint("****** MADlib upgrade error: the dmg image was not mounted properly! ******",
                        sysexit = True)
                
            image = m.group(1)
            try:
                execute_cmd(name = "Installing the meta-package ...",
                            cmdStr = "sudo installer -pkg " + image +
                            "/*pkg -target /Volumes/Macintosh\ HD")
            except:
                biprint("****** MADlib upgrade error: could not install the meta-package! ******",
                        sysexit = True)
            install_dir = cls.dmg_install_dir

            try:
                execute_cmd(name = "Ejecting the dmg image ...",
                            cmdStr = "hdiutil eject " + image)
            except:
                biprint("****** MADlib upgrade error: could not eject the dmg image! ******",
                        sysexit = True)

        return install_dir

    # ----------------------------------------------------------------

    @classmethod
    def validate_params (cls):
        """
        Validate the class variables
        """
        valid = True
        if (cls.old_version is None or
            cls.new_version is None or
            cls.old_version == cls.new_version):
            valid = False

        if (cls.old_file_location is not None and
            cls.new_file_location is not None and
            cls.old_file_location == cls.new_file_location):
            valid = False

        if (cls.old_download_link is not None and
            cls.new_download_link is not None and
            cls.old_download_link == cls.new_download_link):
            valid = False

        if valid is False:
            biprint("****** MADlib upgrade error: some class variable is not correct! ******",
                    sysexit = True)
        
    # ----------------------------------------------------------------

    @classmethod
    def loadTestsFromTestCase (cls):
        """
        Override the superclass class method
        """
        # Super class itself is also executed
        # but we return [] so that an empty set is executed
        if cls.old_version is None:
            return []

        # For testing class, we examine the class variables
        # NOTE: This must be put after the 'return []'
        cls.validate_params()

        cls.sql_dir_tmp = unique_string()
        cls.db_upgrade = unique_string()
        cls.upgrade_dir = unique_string()
            
        tinctest.TINCTestLoader.testMethodPrefix = cls.sql_prefix

        # cls.cwd = os.getcwd() # current working dir

        cls.cleanup = get_env_flag(cls, "CLEANUP", cls.cleanup)
        
        cls.create_ans_ = cls._get_ans_version()

        cls.upgrade_dir = cls._get_upgrade_home()
        cls.old_target_dir = os.path.join(cls.upgrade_dir, "madlib_" + cls.old_version)
        cls.new_target_dir = os.path.join(cls.upgrade_dir, "madlib_" + cls.new_version)

        cls.hosts_file = cls._get_hosts_file()

        skip = get_skip(cls)

        cls.source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(os.path.realpath(cls.source_file))
        cls.load_dir = os.path.join(source_dir, cls.load_dir)
        cls.sql_dir = os.path.join(source_dir, cls.sql_dir)
        # use sql_dir_tmp for test case files
        cls.sql_dir_tmp = os.path.join("/tmp", cls.sql_dir_tmp)
        cls.ans_dir = os.path.join(source_dir, cls.ans_dir)
        cls.out_dir = os.path.join(os.path.dirname(cls.ans_dir),
                                   cls.out_dir_head + cls.__name__)

        make_sure_path_exists(cls, cls.sql_dir)
        make_sure_path_exists(cls, cls.sql_dir_tmp)
        make_sure_path_exists(cls, cls.ans_dir)
        make_sure_path_exists(cls, cls.out_dir)

        cls.msg_head = "Test-upgrade-" + cls.__name__ + "."

        # add skip tag if needed
        for fs in os.listdir(cls.sql_dir):
            if fs.endswith(".sql") and fs.startswith(cls.sql_prefix):
                if fs in skip:
                    w = open(cls.sql_dir_tmp + "/" + fs, "w")
                    with open(fs, "r") as f:
                        w.write("-- @skip Skip this test for upgrading")
                        for line in f:
                            w.write(line)
                    w.close()
                else:
                    execute_cmd("Run command ...", "cp {sql_dir}/{fs} {sql_dir_tmp}/".format(
                        sql_dir = cls.sql_dir, fs = fs,
                        sql_dir_tmp = cls.sql_dir_tmp))

        try:
            cls._init_schema()
            biprint("\n***********************************************************************************")
            if cls.cleanup is False:
                biprint("\n###### All intermediate files are stored in " + cls.upgrade_dir + "/ ######\n")
            else:
                print
                logger.info("============================================================\n")
                logger.info("\n###### All intermediate files are stored in " + cls.upgrade_dir + "/ ######\n")
                logger.info("============================================================\n")
                
            cls.sql_dir = cls.sql_dir_tmp
            if cls.create_ans_ is not False: # to create answer
                if cls.create_ans_ == cls.old_version:
                    pkg_type = cls.old_pkg_type
                    download_link = cls.old_download_link
                    file_location = cls.old_file_location
                    target_dir = cls.old_target_dir
                else:
                    pkg_type = cls.new_pkg_type
                    download_link = cls.new_download_link
                    file_location = cls.new_file_location
                    target_dir = cls.new_target_dir
                # source_name = file_location if file_location is not None else download_link
                msg = cls.msg_head + "Fetching and installing MADlib " + cls.create_ans_ \
                      + " from " + pkg_type  + " ... "
                      # + " from " + source_name  + " ... ", syswrite = True)
                biprint(msg, syswrite = True)
                install_dir = cls._install_MADlib(cls.create_ans_, target_dir,
                                                  pkg_type,
                                                  download_link, file_location, "")

                print
                msg = cls.msg_head + "Deploying MADlib " + cls.create_ans_ + " onto database " +\
                      cls.db_upgrade + " with schema " + cls.schema_upgrade\
                      + " ... "
                biprint(msg, syswrite = True)
                cls._deploy_MADlib("install", install_dir, pkg_type, "")

                print
                biprint(cls.msg_head + "Loading data structure ......")
                cls._run_load() # load the testing data structure
                
                print
                # output answer files
                biprint(cls.msg_head + "Generating answer files ......")
                tests = super(MADlibUpgradeTestCase, cls).loadTestsFromTestCase()
            else:
                # first install the old version
                # source_name = cls.old_file_location if cls.old_file_location \
                #               is not None else cls.old_download_link
                msg = cls.msg_head + "Fetching and installing MADlib " + cls.old_version\
                      + " from " + cls.old_pkg_type + " ... "
                      # + " from " + source_name + " ... "
                biprint(msg, syswrite = True)
                install_dir = cls._install_MADlib(cls.old_version,
                                                  cls.old_target_dir,
                                                  cls.old_pkg_type,
                                                  cls.old_download_link,
                                                  cls.old_file_location, "")

                print
                msg = cls.msg_head + "Deploying MADlib " + cls.old_version + " onto database " +\
                      cls.db_upgrade + " with schema " + cls.schema_upgrade\
                      + " ... "
                biprint(msg, syswrite = True)
                cls._deploy_MADlib("install", install_dir, cls.old_pkg_type, "")
                
                print
                biprint(cls.msg_head + "Loading data structure ......")
                cls._run_load() # load the testing data structure
                print
                # upgrade to the newer version
                # source_name = cls.new_file_location if cls.new_file_location \
                #               is not None else cls.new_download_link
                msg = cls.msg_head + "Fetching and installing MADlib " + cls.new_version\
                      + " from " + cls.old_pkg_type + " ... "
                      # + " from " + source_name + " ... ", syswrite = True)
                biprint(msg, syswrite = True)
                install_dir = cls._install_MADlib(cls.new_version,
                                                  cls.new_target_dir,
                                                  cls.new_pkg_type,
                                                  cls.new_download_link,
                                                  cls.new_file_location, "")

                print
                msg = cls.msg_head + "Upgrading MADlib to " + cls.new_version + " on database " +\
                      cls.db_upgrade + " with schema " + cls.schema_upgrade + " ... "
                biprint(msg, syswrite = True)
                cls._deploy_MADlib("upgrade", install_dir, cls.new_pkg_type, "")

                print
                msg = cls.msg_head + "Checking the version of MADlib ... "
                biprint(msg, syswrite = True)
                cls._check_upgraded_version()

                print
                msg = cls.msg_head + "Running MADlib install-check for upgraded MADlib (this will take 5 ~ 10 minutes) ... "
                biprint(msg, syswrite = True)
                cls._run_installcheck(install_dir) # install check takes a long time

                # call the super class of MADlibTestCase
                # not the super class of this class
                biprint("***********************************************************************************")
                # biprint(cls.msg_head + "Generating result files and comparing with the answer files ......")
                tests = super(MADlibUpgradeTestCase, cls).loadTestsFromTestCase()
        except (KeyboardInterrupt, SystemExit):
            if cls.already_tearDown is False:
                cls.tearDown(True)
            biprint(cls.msg_head + "general interruption ... -9999.99 ms ... FAIL\n")
            biprint("\n\n++++++++++ MADlib upgrade test has been interrupted ! ++++++++++")
            # sys.exit()
            return []

        cls.test_num = len(tests)
        return tests

    # ----------------------------------------------------------------

    def __init__(self, methodName, sql_file = None, db_name = None):
        super(MADlibUpgradeTestCase, self).__init__(methodName, sql_file,
                                                    self.__class__.db_settings_["dbname"])

    # ----------------------------------------------------------------

    @classmethod
    def _init_schema (cls):
        """
        Recreate the schema
        """
        dbname_ext = get_db_name()
        if dbname_ext is None:
            cls.db_name = cls.db_upgrade
        else:
            cls.db_name = dbname_ext
        if cls.db_name is None:
            cls.db_name = os.environ.get("USER")
        execute_cmd(name = "Create database",
                    cmdStr = "dropdb " + cls.db_name +
                    "; createdb " + cls.db_name)
            
        cls.db_settings_ = get_dbsettings(cls.__name__, cls.db_upgrade)
        db = cls.db_settings_

        sql_cmd = """
                  drop schema if exists {schema_upgrade} cascade; 
                  create schema {schema_upgrade};
                  set search_path = {schema_upgrade};
                  """.format(schema_upgrade = cls.schema_upgrade)
        PSQL1.run_sql_command(sql_cmd, 
                              dbname = cls.db_name,
                              username = db["superuser"],
                              password = db["superpwd"],
                              host = db["host"],
                              port = db["port"],
                              PGOPTIONS = db["pg_options"],
                              psql_options = db["psql_options"])
        execute_cmd("Run command ...", "rm -rf " + cls.upgrade_dir)

        if cls.hosts_file is not None:
            execute_cmd(name = "Initialize local RPM database on hosts ...",
                        cmdStr =
                        """
                        gpssh -f {hosts_file} <<EOF
                            rm -rf {upgrade_dir}
                        EOF
                        """.format(upgrade_dir = cls.upgrade_dir,
                                   hosts_file = cls.hosts_file))
        
        # if cls.old_pkg_type == "gppkg":
        #     execute_cmd(name = "gppkg removing old package ...",
        #                 cmdStr = "gppkg -r " + gpmad[cls.old_version[0:3]])
        # if cls.new_pkg_type == "gppkg":
        #     execute_cmd(name = "gppkg removing new package ...",
        #                 cmdStr = "gppkg -r " + gpmad[cls.new_version[0:3]])
        if cls.old_pkg_type == "gppkg" or cls.new_pkg_type == "gppkg":
            execute_cmd("Clean up gpkg database", cmdStr = "gppkg -c")
            res = execute_cmd("Find the installed gppkg",
                              cmdStr = "gppkg -q --all")
            for m in re.finditer(r"(madlib-\d+\.\d+)", str(res)):
                execute_cmd("Remove previous packages",
                            cmdStr = "gppkg -r " + m.group(1))
                
        if cls.old_pkg_type == "dmg" or cls.new_pkg_type == "dmg":
            execute_cmd(name = "Removing previous dmg installations ...",
                        cmdStr = "sudo rm -rf " + cls.dmg_install_dir)
        
    # ----------------------------------------------------------------

    @classmethod
    def _get_schema_upgrade (cls):
        """
        Get the schema that is used to install MADlib
        """
        if os.environ.has_key("SCHEMA"):
            return os.environ.get("SCHEMA")
        else:
            return cls.schema_upgrade

    # ----------------------------------------------------------------

    @classmethod
    def _get_hosts_file (cls):
        """
       	Get the host file name 
       	"""
        if os.environ.has_key("HOSTS"):
            value = os.environ.get("HOSTS")
        else:
            value = cls.hosts_file

        if value is None:
            return None

        if os.path.exists("./" + value):
            return os.path.realpath("./" + value)
        elif os.path.exists(value):
            return os.path.realpath(value)
        
        cls_path = os.path.dirname(os.path.realpath(sys.modules[cls.__module__].__file__))
        target = os.path.join(cls_path, value)
        if os.path.exists(target):
            return target
        else:
            cls.tearDown(True)
            biprint(cls.msg_head + "get_hosts_file ... -9999.99 ms ... FAIL\n")
            biprint("****** MADlib upgrade error: no such hosts file! ******",
                    sysexit = True)

    # ----------------------------------------------------------------

    # download binary package
    @classmethod
    def _download_binary (cls, target_dir, version, download_link, msg):
        logger.info("Downloading binary ...")
        if download_link is None:
            cls.tearDown(True)
            biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
            biprint("****** MADlib Upgrade Error: Please provide the download link for MADlib " +
                    version + " ******", sysexit = True)
            
        filename = download_link.split("/")[-1]
        urllib.urlretrieve(download_link, target_dir + "/" + filename)
                
        return (target_dir, filename)

    # ----------------------------------------------------------------

    # download source package
    @classmethod
    def _download_source (cls, target_dir, version, download_link, msg):
        """
        Download source, return the directory
        """
        logger.info("Downloading source ...")
        if download_link is None:
            cls.tearDown(True)
            biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
            biprint("****** MADlib Upgrade Error: Please provide the download link for MADlib " +
                    version + " ******", sysexit = True)
        #    download_link = "https://github.com/madlib/madlib/tarball/v" \
        #            + version + "/"

        filename = "madlib.tar.gz"
        execute_cmd("Run command ...", "mkdir -p {target}".format(target = target_dir))
        execute_cmd("Run command ...", "cd " + target_dir + "; wget -c " + 
                    download_link + " --no-check-certificate -O " + filename)
                
        return (target_dir, filename)

    # ----------------------------------------------------------------

    @classmethod
    def _deploy_MADlib (cls, action, install_dir, pkg_type, msg):
        """
        Deploy the MADlib onto the DBMS
        """
        t0 = time.time()
        # pick the test case specific schema 
        if cls.hosts_file is None or pkg_type != "source":
            res = cls._run_madpack(action, install_dir)
            if re.search(": ERROR :", str(res)) is not None:
                biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
                biprint("\n---------------------------------------------------------")
                biprint("FAILED: could not " + action + " MADlib")
                biprint("---------------------------------------------------------\n")
                biprint("****** MADlib upgrade error: could not " + action + " ******",
                        sysexit = True)
        else: 
            cls._deploy_on_cluster(action, install_dir, msg)
        t1 = time.time()
        biprint(msg + "%.2f ms ... ok\n" % (int((t1 - t0) * 100000)/100.), syswrite = True)

    # ----------------------------------------------------------------

    @classmethod
    def _run_madpack (cls, action, install_dir):
        """
        run madpack command
        """
        db = cls.db_settings_
        if db["superpwd"] is None:
            db["superpwd"] = ""
        if db["superuser"] is None:
            db["superuser"] = os.environ.get("USER")
        if db["port"] is None:
            if os.environ.has_key("PGPORT"):
                db["port"] = os.environ.get("PGPORT")
            else:
                db["port"] = 5432
        result = execute_cmd(name = "Deploy MADlib ...",
                             cmdStr = "{install_dir}/bin/madpack -p {kind} \
                             -s {schema_upgrade} -c {superuser}/{superpwd}@localhost:{port}/{dbname} {action}".format(
                                 install_dir = install_dir,
                                 kind = db["kind"],
                                 schema_upgrade = cls.schema_upgrade,
                                 superuser = db["superuser"],
                                 superpwd = db["superpwd"],
                                 port = db["port"],
                                 dbname = cls.db_name,
                                 action = action))
        return result
    
    # ----------------------------------------------------------------

    @classmethod
    def tearDown (cls, goahead = False):
        """
        After the test, remove MADlib installation
        """
        if cls.cleanup is False:
            return
            
        if goahead is False:
            if cls.old_version is None:
                return
            cls.test_count += 1
            if cls.test_count < cls.test_num:
                return

        logger.info(
            """
            
            ########################################################################
            {class_name} Tear down the intermediate files, schema, installations ...
            ########################################################################
            
            """.format(class_name = cls.__name__))
        
            
        os.chdir(cls.cwd) # get back to the original working dir
        # db = cls.db_settings_
        # sql_cmd = "drop schema if exists {schema_upgrade} cascade;"\
        #            .format(schema_upgrade = cls.schema_upgrade)
        # PSQL1.run_sql_command(sql_cmd,
        #                       dbname = db["dbname"],
        #                       username = db["superuser"],
        #                       password = db["superpwd"],
        #                       host = db["host"],
        #                       port = db["port"],
        #                       PGOPTIONS = db["pg_options"],
        #                       psql_options = db["psql_options"])

        execute_cmd("Drop working database", "dropdb " + cls.db_name)
        
        execute_cmd("Run command ...", "rm -rf " + cls.sql_dir_tmp)
        execute_cmd("Run command ...", "rm -rf " + cls.upgrade_dir)
        if cls.new_pkg_type == "dmg" or cls.old_pkg_type == "dmg":
            execute_cmd("Run command ...", "sudo rm -rf " + cls.dmg_install_dir)
        if cls.hosts_file is None:
            if cls.old_pkg_type == "gppkg":
                execute_cmd(name = "gppkg removing old package ...",
                            cmdStr = "gppkg -r " + gpmad[cls.old_version[0:3]])
            if cls.new_pkg_type == "gppkg":
                execute_cmd(name = "gppkg removing new package ...",
                            cmdStr = "gppkg -r " + gpmad[cls.new_version[0:3]])
        else:
            execute_cmd(name = "Removing intermediate folder on hosts ...",
                        cmdStr = """
                        gpssh -f {hosts_file} << EOF
                            rm -rf {upgrade_dir}
                        EOF
                        """.format(hosts_file = cls.hosts_file,
                                 upgrade_dir = cls.upgrade_dir))
        cls.already_tearDown = True
        
    # ----------------------------------------------------------------

    @classmethod
    def _run_load (cls):
        """
        Run all the load SQL files in the directory provided
        @param workload_dir: the location of the workload folder
        @type  workload_dir: String
        """
        db = cls.db_settings_
        logger.info("Running workload ...")
        for f in os.listdir(cls.load_dir):
            if f.endswith(".sql") and f.startswith(cls.load_prefix):
                t0 = time.time()
                res =  PSQL1.run_sql_file(sql_file = cls.load_dir + "/"
                                          + f,
                                          dbname = cls.db_name,
                                          username = db["superuser"],
                                          password = db["superpwd"],
                                          host = db["host"],
                                          port = db["port"],
                                          PGOPTIONS = db["pg_options"],
                                          psql_options = db["psql_options"],
                                          output_to_file = False)
                t1 = time.time()
                if res:
                    biprint(cls.msg_head + "loading " + f + " ... %.2f ms ... ok" % (int((t1 - t0) * 100000)/100.))
                else:
                    biprint(cls.msg_head + "loading " + f + " ... -9999.99 ms ... FAIL")
                    cls.tearDown(True)
                    biprint("\n****** MADlib upgrade error: cannot load " + f + " ******", sysexit = True)
         
    # ----------------------------------------------------------------

    # Actually run the test
    def _run_test (self, sql_file, ans_file):
        """
        Validate that the workload were executed successfully
        @param workload_dir: the location of the workload folder
        @type  workload_dir: String
        @param use_diff_ans_file: diff the ans file and the out file or not
        @type  use_diff_ans_file: Boolean
        """
        logger.info("Validating workload ...")
        sql_resultfile = os.path.join(self.get_out_dir(),
                                      os.path.basename(sql_file) + ".out")
        db = self.__class__.db_settings_
        PSQL1.run_sql_file(sql_file = sql_file,
                           out_file = sql_resultfile,
                           dbname = self.__class__.db_name,
                           username = db["superuser"],
                           password = db["superpwd"],
                           host = db["host"],
                           port = db["port"],
                           PGOPTIONS = db["pg_options"],
                           psql_options = db["psql_options"])

        # First run to create the baseline file
        if self.__class__.create_ans_:
            shutil.copyfile(sql_resultfile, ans_file)
            os.remove(sql_resultfile)
            biprint ("Answer file was created")
            return True

        return self.validate(sql_resultfile, ans_file)

    # ----------------------------------------------------------------

    @classmethod
    def _check_upgraded_version (cls, msg = ""):
        """
        Check that the installed MADlib version is correct
        """
        logger.info("Checking MADlib version installed ...")
        version_str = ""
        try:
            with dbconn.connect(dbconn.DbURL(
                    dbname = cls.db_name,
                    port = cls.db_settings_["port"])) as conn:
                query = "select " + cls.schema_upgrade + ".version()"
                t0 = time.time()
                row = dbconn.execSQLForSingleton(conn, query)
                version_str = row.split(" ").pop(2).strip(",")
                t1 = time.time()
            if version_str == cls.new_version:
                biprint(msg + "%.2f ms ... ok\n" % (int((t1 - t0) * 100000)/100.), syswrite = True)
                biprint("\n---------------------------------------------------------")
                biprint("Successfully upgraded MADlib version from "
                      + cls.old_version + " to " + cls.new_version)
                biprint("---------------------------------------------------------\n")
            else:
                biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
                biprint("\n---------------------------------------------------------")
                biprint("FAILED: could not upgrade MADlib version from "
                      + cls.old_version + " to " + cls.new_version)
                biprint("---------------------------------------------------------\n")
                cls.tearDown(True)
                biprint("****** MADlib upgrade error: could not upgrade from "
                         + cls.old_version
                         + " to " + cls.new_version + " ******", sysexit = True)
        except:
            biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
            cls.tearDown(True)
            biprint("****** MADlib upgrade error: could not upgrade from "
                     + cls.old_version
                     + " to " + cls.new_version + " ******", sysexit = True)

    # ----------------------------------------------------------------

    @classmethod
    def _run_installcheck (cls, install_dir, msg = ""):
        """
        Run install check
        """
        t0 = time.time()
        res = cls._run_madpack("install-check", install_dir)
        t1 = time.time()
        msg = msg + "%.2f ms " % (int((t1 - t0) * 100000)/100.)
        if re.search("\|FAIL\|", str(res)) is not None or t1 - t0 < 10.:
            biprint(msg + "... FAIL\n", syswrite = True)
            biprint("\n---------------------------------------------------------")
            biprint("FAILED: The install-check of new version " + cls.new_version)
            biprint("        Please see the log file for details.")
            biprint("---------------------------------------------------------\n")
        else:
            biprint(msg + "... ok\n", syswrite = True)
            biprint("\n---------------------------------------------------------")
            biprint("PASSED: The install-check of new version " + cls.new_version)
            biprint("---------------------------------------------------------\n")
        return
        
    # ----------------------------------------------------------------

    @classmethod
    def _deploy_on_cluster (cls, action, install_dir, msg):
        """
        Deploy MADlib on a cluster
        """        
        db = cls.db_settings_
        os.chdir(install_dir + "/..")

        if db["superpwd"] is None:
            db["superpwd"] = ""
        if db["superuser"] is None:
            db["superuser"] = os.environ.get("USER")
        if db["port"] is None:
            if os.environ.has_key("PGPORT"):
                db["port"] = os.environ.get("PGPORT")
            else:
                db["port"] = 5432

        execute_cmd(name = "Distributing MADlib package ...", cmdStr =
            """
            tar czf madlib.tar.gz madlib;
            gpssh -f {hosts_file} <<EOF
                mkdir -p $(pwd)
            EOF
            """.format(hosts_file = cls.hosts_file))
        # ------------------------------------------------
        execute_cmd(name = "Scp package to hosts ...",
                      cmdStr = 'gpscp -f {hosts_file} \
                      madlib.tar.gz "=:$(pwd)"'.format(hosts_file = cls.hosts_file))
        # ------------------------------------------------
        execute_cmd(name = "Expand the epackage ...", cmdStr =
            """
            gpssh -f {hosts_file} <<EOF
                cd $(pwd);
                tar zxf madlib.tar.gz;
            EOF
            """.format(hosts_file = cls.hosts_file))
        # ------------------------------------------------
        res = execute_cmd(name = "Deploy on GPDB cluster ...",
                          cmdStr = "cd madlib/; \
                          ./bin/madpack -p greenplum -c \
                          {superuser}/{superpwd}@localhost:{port}/{db}\
                          -s {schema_upgrade} \
                          {action}".format(superuser = db["superuser"],
                                           superpwd = db["superpwd"],
                                           port = db["port"],
                                           db = cls.db_name,
                                           schema_upgrade = cls.schema_upgrade,
                                           action = action))
        if re.search(": ERROR :", str(res)) is not None:
            biprint(msg + "-9999.99 ms ... FAIL\n", syswrite = True)
            biprint("\n---------------------------------------------------------")
            biprint("FAILED: could not " + action + " MADlib on cluster")
            biprint("---------------------------------------------------------\n")
            biprint("****** MADlib upgrade error: could not " + action
                    + " on cluster ******", sysexit = True)

    # ----------------------------------------------------------------------

    def validate (self, outfile, ansfile):
        """
        default validate function is a simple file diff
        """
        return Gpdiff.are_files_equal(outfile, ansfile)
