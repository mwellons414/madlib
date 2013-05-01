
# ------------------------------------------------------------------------
# Upgrade test for MADlib
# ------------------------------------------------------------------------

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.template.lib import PSQL1
from madlib.src.test_utils.get_dbsettings import get_dbsettings
from madlib.src.test_utils.utils import unique_string
from tinctest.lib import Gpdiff
import tinctest
from tinctest import logger
from gppylib.db import dbconn
from gppylib.commands.base import Command
import urllib
import shutil
import os
import re
import sys
import datetime

# ------------------------------------------------------------------------

class MADlibUpgradeTestCase (MADlibTestCase):
    """
    Base class for an upgrade test case
    """
    eigen_pkg = None # if you cannot download eigen package
    
    load_dir = "load" # create testing data structure
    load_prefix = "" # load files start with this string

    sql_dir = "sql" # test case folder
    sql_dir_tmp = unique_string() 
    sql_prefix = "" # test cases start with this string
    ans_dir = "expected"
    out_dir = "result"
    
    hosts_file = None
    allowed_pkg_type = ["source", "rpm", "gppkg"]

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
    
    skip_file = "skip.py"
    db_settings_ = get_dbsettings("MADlibUpgradeTestCase")
    
    # can control from environment variable
    schema_upgrade = "upgrade_madlib"
    skip = []
    create_ans_ = False

    upgrade_dir = "upgrade_home"

    # the current working dir
    working_dir = os.path.abspath(".")

    test_count = 0

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
            print("****** MADlib upgrade error: package type is not supported! ******")
            sys.exit("****** package type must be source, rpm or gppkg! ******")

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
                sys.exit("****** MADlib upgrade test error: " +
                         cls.__module__ + "." + cls.__name__ +
                         " can only create answers for versions of " +
                         cls.old_version + " and " + cls.new_version
                         + " ******")
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
                return os.path.abspath("./" + value)
            elif os.path.exists(value):
                return os.path.abspath(value)
        else:
            value = cls.upgrade_dir
            
        cls_path = os.path.dirname(os.path.abspath(sys.modules[cls.__module__].__file__))
        target = os.path.join(cls_path, value)
        if os.path.exists(target):
            return target
        else:
            try:
                # os.system("mkdir {target}".format(target = target))
                cmd = Command(name = "mkdir target",
                              cmdStr = "mkdir {target}".format(target = target))
                logger.info("Create the previously non-existing upgrade_home folder ...")
                cmd.run(validateAfter = False)
                result = cmd.get_results()
                logger.info("Output - %s" %result)
                return target
            except:
                sys.exit("****** MADlib Upgrade Error: no such directory for installing MADlib! ******")

            
    # ----------------------------------------------------------------

    # download MADlib package and install it on /usr/local/madlib
    @classmethod
    def _install_MADlib(cls, version, target_dir, pkg_type,
                        download_link = None,
                        file_location = None):
        os.system("mkdir -p " + target_dir)
        logger.info("Starting the install for new MADlib ...")
        logger.info("----------------------------------------")
        if file_location is None:
            if pkg_type == "rpm" or pkg_type == "gppkg":
                install_file = cls._download_binary(version, target_dir,
                                                    download_link)
                # check_md5sum (install_file, version)
            elif pkg_type == "source":
                install_file = cls._download_source(version, target_dir,
                                                    download_link)
                # check_md5sum (install_file, version)
            else:
                cls.tearDown(True)
                sys.exit("****** MADlib Upgrade Error: no such package type (only 'rpm', 'gppkg' and 'source')! ******")
        else:
            if target_dir != os.path.abspath(os.path.dirname(file_location)):
                try:
                    os.system("cp " + file_location + " " + target_dir)
                    install_file = os.path.join(target_dir,
                                                os.path.basename(file_location))
                except:
                    cls.tearDown(True)
                    sys.exit(file_location + " does not exist!")
            else:
                install_file = file_location

        return cls._unzip_download_and_install(install_file, pkg_type, target_dir)

    # ----------------------------------------------------------------

    # uncompress MADlib package and install at /usr/local/madlib
    @classmethod
    def _unzip_download_and_install (cls, install_file, pkg_type, target_dir):
        target_dir = os.path.dirname(install_file)
        if pkg_type == "source":
            logger.info("Untar source package ...")
            try:
                os.chdir(target_dir)
                os.system("rm -rf madlib; mkdir madlib; tar zxf " + 
                          install_file + " -C madlib")
                os.chdir("madlib")
                while "CMakeLists.txt" not in os.listdir("."):
                    dir_name = os.listdir(".")[0]
                    os.chdir(dir_name)

                cmd = Command(name = "Build MADlib",
                              cmdStr = "./configure")
                logger.info("Building MADlib ...")
                cmd.run(validateAfter = False)
                result = cmd.get_results()
                logger.info("""
                            -------------------------- Output ------------------------- 
                            %s
                            """ % result)

                if cls.eigen_pkg is not None:
                    os.system("cp " + cls.eigen_pkg + " build/third_party/downloads/")
                cmd = Command(name = "Continue building",
                              cmdStr = "cd build; make")
                cmd.run(validateAfter = False)
                result = cmd.get_results()
                logger.info("""
                            %s
                            -----------------------------------------------------------
                            """ % result)
                
                install_dir = os.path.abspath("./build/src")
                os.chdir(cls.working_dir)
            except:
                cls.tearDown(True)
                sys.exit("****** MADlib Upgrade Error: cannot uncompress the tar.gz source package! ******")
        elif pkg_type == "rpm":
            logger.info("Uncompress RPM package ...")
            try:
                os.chdir(target_dir)
                cmd = Command(name = "Expand RPM package",
                              cmdStr = "rpm2cpio " + install_file +
                              " | cpio -idmv")
                logger.info("Uncompress RPM package ...")
                cmd.run(validateAfter = False)
                result = cmd.get_results()
                logger.info("""
                    ----------------------- Output --------------------- 
                    %s
                    ----------------------------------------------------
                    """ % result)
                install_dir = os.path.join(target_dir,
                                           "usr/local/madlib")
            except:
                cls.tearDown(True)
                sys.exit("****** MADlib Upgrade Error: cannot install the .rpm binary packages! ******")
        elif pkg_type == "gppkg":
            install_dir = install_file

        return install_dir
            
    # ----------------------------------------------------------------

    @classmethod
    def loadTestsFromTestCase (cls):
        """
        Override the superclass class method
        """
        if cls.old_version is None:
            return []

        tinctest.TINCTestLoader.testMethodPrefix = cls.sql_prefix

        cls.cwd = os.getcwd() # current working dir
        
        cls.create_ans_ = cls._get_ans_version()

        cls.upgrade_dir = cls._get_upgrade_home()
        cls.old_target_dir = os.path.join(cls.upgrade_dir, "madlib_" + cls.old_version)
        cls.new_target_dir = os.path.join(cls.upgrade_dir, "madlib_" + cls.new_version)

        cls.hosts_file = cls._get_hosts_file()

        (skip, skip_name) = cls._get_skip()

        cls.source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(cls.source_file))
        cls.load_dir = os.path.join(source_dir, cls.load_dir)
        cls.sql_dir = os.path.join(source_dir, cls.sql_dir)
        # use sql_dir_tmp for test case files
        cls.sql_dir_tmp = os.path.join("/tmp", cls.sql_dir_tmp)
        cls.ans_dir = os.path.join(source_dir, cls.ans_dir)
        cls.out_dir = os.path.join(source_dir, cls.out_dir)

        cls._make_sure_path_exists(cls.sql_dir)
        cls._make_sure_path_exists(cls.sql_dir_tmp)
        cls._make_sure_path_exists(cls.ans_dir)
        cls._make_sure_path_exists(cls.out_dir)

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
                    os.system("cp {sql_dir}/{fs} {sql_dir_tmp}/".format(
                        sql_dir = cls.sql_dir, fs = fs,
                        sql_dir_tmp = cls.sql_dir_tmp))
 
        cls._init_schema()
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
            source_name = file_location if file_location is not None else download_link
            print("* Fetching and installing MADlib " + cls.create_ans_
                  + " from " + source_name  + " ......")
            install_dir = cls._install_MADlib(cls.create_ans_, target_dir,
                                              pkg_type,
                                              download_link, file_location)
            print("* Deploying MADlib " + cls.create_ans_ + " onto database " +
                  cls.db_settings_["dbname"] + " with schema " + cls.schema_upgrade
                  + " ......")
            cls._deploy_MADlib("install", install_dir, pkg_type)
            print("* Loading data structure ......")
            cls._run_load() # load the testing data structure
            # output answer files
            print("* Generating answer files ......")
            tests = super(MADlibTestCase, cls).loadTestsFromTestCase()
        else:
            # first install the old version
            source_name = cls.old_file_location if cls.old_file_location \
                          is not None else cls.old_download_link
            print("* Fetching and installing MADlib " + cls.old_version
                  + " from " + source_name + " ......")
            install_dir = cls._install_MADlib(cls.old_version,
                                              cls.old_target_dir,
                                              cls.old_pkg_type,
                                              cls.old_download_link,
                                              cls.old_file_location)
            print("* Deploying MADlib " + cls.old_version + " onto database " +
                  cls.db_settings_["dbname"] + " with schema " + cls.schema_upgrade
                  + " ......")
            cls._deploy_MADlib("install", install_dir, cls.old_pkg_type)
            print("* Loading data structure ......")
            cls._run_load() # load the testing data structure

            # upgrade to the newer version
            source_name = cls.new_file_location if cls.new_file_location \
                          is not None else cls.new_download_link
            print("* Fetching and installing MADlib " + cls.new_version
                  + " from " + source_name + " ......")
            install_dir = cls._install_MADlib(cls.new_version,
                                              cls.new_target_dir,
                                              cls.new_pkg_type,
                                              cls.new_download_link,
                                              cls.new_file_location)
            print("* Upgrading MADlib to " + cls.new_version + " on database " +
                  cls.db_settings_["dbname"] + " with schema " + cls.schema_upgrade
                  + " ......")            
            cls._deploy_MADlib("upgrade", install_dir, cls.new_pkg_type)
            sys.stdout.write("* Checking the version of MADlib ......")
            sys.stdout.flush()
            cls._check_upgraded_version()
            sys.stdout.write("* Running MADlib install-check for the new version ......")
            sys.stdout.flush()
            cls._run_installcheck(install_dir)
            # call the super class of MADlibTestCase
            # not the super class of this class
            print("* Generating result files and comparing with the answer files ......")
            tests = super(MADlibTestCase, cls).loadTestsFromTestCase()

        cls.test_num = len(tests)
        return tests

    # ----------------------------------------------------------------

    def __init__(self, methodName, sql_file = None, db_name = None):
        super(MADlibTestCase, self).__init__(methodName, sql_file,
                                             self.__class__.db_settings_["dbname"])

    # ----------------------------------------------------------------

    @classmethod
    def _init_schema (cls):
        """
        Recreate the schema
        """
        db = cls.db_settings_
        sql_cmd = """
                  drop schema if exists {schema_upgrade} cascade; 
                  create schema {schema_upgrade};
                  set search_path = {schema_upgrade};
                  """.format(schema_upgrade = cls.schema_upgrade)
        PSQL1.run_sql_command(sql_cmd, 
                              dbname = db["dbname"],
                              username = db["superuser"],
                              password = db["superpwd"],
                              host = db["host"],
                              port = db["port"],
                              PGOPTIONS = db["pg_options"],
                              psql_options = db["psql_options"])
        os.system("rm -rf " + cls.upgrade_dir)        
        
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
            return os.path.abspath("./" + value)
        elif os.path.exists(value):
            return os.path.abspath(value)
        
        cls_path = os.path.dirname(os.path.abspath(sys.modules[cls.__module__].__file__))
        target = os.path.join(cls_path, value)
        if os.path.exists(target):
            return target
        else:
            cls.tearDown(True)
            sys.exit("****** MADlib upgrade error: no such hosts file! ******")

    # ----------------------------------------------------------------

    # download binary package
    @classmethod
    def _download_binary (cls, target_dir, version, download_link):
        logger.info("Downloading binary ...")
        if download_link is None:
            cls.tearDown(True)
            sys.exit("****** MADlib Upgrade Error: Please provide the download link for MADlib " +
                     version + " ******")
            
        filename = download_link.split("/")[-1]
        urllib.urlretrieve(download_link, target_dir + "/" + filename)
                
        return (target_dir, filename)

    # ----------------------------------------------------------------

    # download source package
    @classmethod
    def _download_source (cls, target_dir, version, download_link):
        """
        Download source, return the directory
        """
        logger.info("Downloading source ...")
        if download_link is None:
            cls.tearDown(True)
            sys.exit("****** MADlib Upgrade Error: Please provide the download link for MADlib " +
                     version + " ******")
        #    download_link = "https://github.com/madlib/madlib/tarball/v" \
        #            + version + "/"

        filename = "madlib.tar.gz"
        os.system("mkdir -p {target}".format(target = target_dir))
        os.system("cd " + target_dir + "; wget -c " + 
                  download_link + " --no-check-certificate -O " + filename)
                
        return (target_dir, filename)

    # ----------------------------------------------------------------

    @classmethod
    def _deploy_MADlib (cls, action, install_dir, pkg_type):
        """
        Deploy the MADlib onto the DBMS
        """
        # pick the test case specific schema 
        if cls.hosts_file is None:
            if pkg_type != "gppkg":
                cls._run_madpack(action, install_dir)
            else:
                gppkg_file = install_dir # the file
                #opt = "-i" if action == "install" else "-u"
                opt = "-i"
                cmd = Command(name = "Installing gppkg for MADlib",
                              cmdStr = "gppkg " + opt + " " + gppkg_file)
                logger.info("Deploying MADlib onto database ...")
                cmd.run(validateAfter = False)
                result = cmd.get_results()
                logger.info("""
                    ------------------------- Output ----------------------
                    %s
                    -------------------------------------------------------
                    """ % result)
        else: 
            cls._deploy_on_cluster(action, install_dir, pkg_type)

    # ----------------------------------------------------------------

    @classmethod
    def _run_madpack (cls, action, install_dir):
        """
        run madpack command
        """
        db = cls.db_settings_
        if db["superpwd"] is None:
            superpwd = ""
        cmd = Command(name = "Deploy MADlib",
                      cmdStr = "{install_dir}/bin/madpack -p {kind} \
                      -s {schema_upgrade} -c {superuser}/{superpwd}@localhost:{port}/{dbname} {action}".format(
                          install_dir = install_dir,
                          kind = db["kind"],
                          schema_upgrade = cls.schema_upgrade,
                          superuser = db["superuser"],
                          superpwd = superpwd,
                          port = db["port"],
                          dbname = db["dbname"],
                          action = action))
        logger.info("Deploying MADlib onto the testing database ...")
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        logger.info("""
                    ----------------------- Output --------------------- 
                    %s
                    ----------------------------------------------------
                    """ % result)
        return result
    
    # ----------------------------------------------------------------

    @classmethod
    def tearDown (cls, cleanup = False):
        """
        After the test, remove MADlib installation
        """
        if cleanup is False:
            if cls.old_version is None:
                return
            cls.test_count += 1
            if cls.test_count < cls.test_num:
                return
                
        os.chdir(cls.cwd) # get back to the original working dir
        db = cls.db_settings_
        sql_cmd = "drop schema if exists {schema_upgrade} cascade;"\
                   .format(schema_upgrade = cls.schema_upgrade)
        PSQL1.run_sql_command(sql_cmd,
                              dbname = db["dbname"],
                              username = db["superuser"],
                              password = db["superpwd"],
                              host = db["host"],
                              port = db["port"],
                              PGOPTIONS = db["pg_options"],
                              psql_options = db["psql_options"])
        os.system("rm -rf " + cls.upgrade_dir)
        os.system("rm -rf " + cls.sql_dir_tmp)
        
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
                sys.stdout.write("  -- loading " + f + " ...... ")
                res =  PSQL1.run_sql_file(sql_file = cls.load_dir + "/"
                                          + f,
                                          dbname = db["dbname"],
                                          username = db["superuser"],
                                          password = db["superpwd"],
                                          host = db["host"],
                                          port = db["port"],
                                          PGOPTIONS = db["pg_options"],
                                          psql_options = db["psql_options"],
                                          output_to_file = False)
                if res:
                    sys.stdout.write("ok\n")
                else:
                    cls.tearDown(True)
                    sys.exit("\n****** MADlib upgrade error: cannot load " + f + " ******")
         
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
                           dbname = db["dbname"],
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
            print "Answer file was created"
            return True

        return self.validate(sql_resultfile, ans_file)

    # ----------------------------------------------------------------

    @classmethod
    def _check_upgraded_version (cls):
        """
        Check that the installed MADlib version is correct
        """
        logger.info("Checking MADlib version installed ...")
        version_str = ""
        try:
            with dbconn.connect(dbconn.DbURL(
                    dbname = cls.db_settings_["dbname"],
                    port = cls.db_settings_["port"])) as conn:
                query = "select " + cls.schema_upgrade + ".version()"
                row = dbconn.execSQLForSingleton(conn, query)
                version_str = row.split(" ").pop(2).strip(",")
            if version_str == cls.new_version:
                sys.stdout.write(" ok\n")
                print("\n---------------------------------------------------------")
                print("Successfully upgraded MADlib version from "
                      + cls.old_version + " to " + cls.new_version)
                print("---------------------------------------------------------\n")
        except:
            sys.stdout.write(" FAIL\n")
            cls.tearDown(True)
            sys.exit("****** MADlib upgrade error: could not upgrade from "
                     + cls.old_version
                     + " to " + cls.new_version + " ******")

    # ----------------------------------------------------------------

    @classmethod
    def _run_installcheck (cls, install_dir):
        """
        Run install check
        """
        t1 = datetime.datetime.now()
        res = cls._run_madpack("install-check", install_dir)
        t2 = datetime.datetime.now()
        sys.stdout.write(" %ss ......" %
                         str(int(t2.strftime('%s')) - int(t1.strftime('%s'))))
        if re.search("\|FAIL\|", str(res)) is not None:
            sys.stdout.write(" FAIL\n")
            print("\n---------------------------------------------------------")
            print("FAILED: The install-check of new version " + cls.new_version)
            print("        Please see the log file for details.")
            print("---------------------------------------------------------\n")
        else:
            sys.stdout.write(" ok\n")
            print("\n---------------------------------------------------------")
            print("PASSED: The install-check of new version " + cls.new_version)
            print("---------------------------------------------------------\n")
        
    # ----------------------------------------------------------------

    @classmethod
    def _deploy_on_cluster (cls, action, install_dir, pkg_type):
        """
        Deploy MADlib on a cluster
        """
        if cls.hosts_file is None:
            cls.tearDown(True)
            sys.exit("****** MADlib upgrade error: please specify the hosts file! ******")
        
        db = cls.db_settings_
        os.chdir(install_dir + "/..")

        folder = "src" if pkg_type == "source" else "madlib"
        
        cmd = Command(name = "Distributing MADlib package", cmdStr =
            """
            cp -r {folder} madlib_compiled;   
            tar czf madlib_compiled.tar.gz madlib_compiled;
            gpssh -f {hosts_file} <<EOF
                rm -rf $(pwd)
                mkdir -p $(pwd)
            EOF
            """.format(hosts_file = cls.hosts_file, folder = folder))
        logger.info("Distributing MADlib package")
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        logger.info("""
                    ------------------------- Output ----------------------
                    %s                    
                    """ % result)
        # ------------------------------------------------
        cmd = Command(name = "Scp package to hosts",
                      cmdStr = 'gpscp -f {hosts_file} \
                      madlib_compiled.tar.gz "=:$(pwd)"'.format(hosts_file = cls.hosts_file))
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        logger.info("%s" % result)
        # ------------------------------------------------
        cmd = Command(name = "Expand the epackage", cmdStr =
            """
            gpssh -f {hosts_file} <<EOF
                cd $(pwd);
                tar zxf madlib_compiled.tar.gz;
                rm madlib_compiled.tar.gz;
            EOF
            """.format(hosts_file = cls.hosts_file))
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        logger.info("%s" % result)
        # ------------------------------------------------
        cmd = Command(name = "Deploy on GPDB cluster",
                      cmdStr = "cd madlib_compiled/; \
                      ./bin/madpack -p greenplum -c \
                      {superuser}/{superpwd}@localhost:{port}/{db}\
                      -s {schema_upgrade} \
                      {action}".format(superuser = db["superuser"],
                                       superpwd = db["superpwd"],
                                       port = db["port"],
                                       db = db["dbname"],
                                       schema_upgrade = cls.schema_upgrade,
                                       action = action))
        logger.info("Deploying MADlib onto GPDB cluster ...")
        cmd.run(validateAfter = False)
        result = cmd.get_results()
        logger.info("""
                    ------------------------- Output ----------------------
                    %s
                    -------------------------------------------------------
                    """ % result)

    # ----------------------------------------------------------------------

    def validate (self, outfile, ansfile):
        """
        default validate function is a simple file diff
        """
        return Gpdiff.are_files_equal(outfile, ansfile)
                     
