import datetime
import inspect
import new
import os
import re
import sys

import unittest2 as unittest
from fnmatch import fnmatch

import tinctest

from tinctest import TINCTestLoader
from tinctest.datagen.databases import __databases__
from tinctest.models.gpdb import GPDBTestCase
from tinctest.models.perf import PerformanceTestCase
from tinctest.runner import TINCTextTestResult
from tinctest.models.concurrency import ConcurrencyTestCase
from tinctest.lib import Gpdiff, PSQL, collect_gpdb_logs
from gppylib.gparray import GpArray
from gppylib.db.dbconn import DbURL

# ------------------------------------------------------------------------

class MADlibSQLTestCase(GPDBTestCase):
    """
	SQLTestCase consumes a SQL file and expected output, performs
	the psql, and returns success/failure based on the ensuing gpdiff.
    """

    # Relative path w.r.t test module, where to look for sql files and ans files.
    # Sub-classes can override this to specify a different location.
    sql_dir = ''
    ans_dir = ''
    out_dir = ''

    # ----------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))
        abs_out_dir = os.path.join(source_dir, cls.out_dir)
        if cls.out_dir and not os.path.exists(abs_out_dir):
            os.makedirs(abs_out_dir)

    # ----------------------------------------------------------------
            
    def __init__(self, methodName, sql_file=None, db_name = None):
        """
        This is an unconventional constructor. By design, the methodName may be
        implicit and may not yet exist in the class definition of whomever is
        subclassing SQLTestCase.

        So, our approach is to discover the intended test method and dynamically
        generate it; then, we will defer to traditional construction in the parent.
        """

        # Test case metadata
        self.db_name = db_name
        self.username = None
        self.gucs = None
        
        self.sql_file = sql_file
        self.ans_file = None
        self._gpdb_seg_log_file = None

        # if the test method is explicit and already defined, construction is trivial
        if methodName.startswith(tinctest.TINCTestLoader.testMethodPrefix) and \
           hasattr(self.__class__, methodName) and \
           hasattr(getattr(self.__class__, methodName), '__call__'): 
            super(MADlibSQLTestCase, self).__init__(methodName)
            return
 
        # otherwise, do dynamic test generation
        assert methodName.startswith(tinctest.TINCTestLoader.testMethodPrefix)
        # partial_test_name = methodName[len(tinctest.TINCTestLoader.testMethodPrefix):]
        partial_test_name = methodName
        
        # implicit sql tests are generated from *.sql/*.ans files 
        # found in the current working directory
        
        # To enable tinc_client to construct a test case for a specific sql file
        # if sql_file is not None:
        #     self.sql_file = sql_file
        #     partial_file_name = os.path.basename(sql_file)[:-4]
        #     # Order in which ans files are located
        #     # 1. Same as sql file location. 2. sql_file/../expected/
        #     # self.ans_file = os.path.join(os.path.dirname(sql_file), "%s.ans" %partial_file_name)
        #     # if not os.path.exists(self.ans_file):
        #     self.ans_file = os.path.join(os.path.dirname(sql_file), "../expected/", "%s.ans" %partial_file_name)

        # else:
        source_file = sys.modules[self.__class__.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))
        sql_dir = os.path.join(self.get_source_dir(), self.__class__.sql_dir)
        ans_dir = os.path.join(self.get_source_dir(), self.__class__.ans_dir)
        self.sql_file = os.path.join(sql_dir, "%s.sql" % partial_test_name)
        self.ans_file = os.path.join(ans_dir, "%s.ans" % partial_test_name)

        if not os.path.exists(self.sql_file):
            raise MADlibSQLTestCaseException('sql file for this test case does not exist - %s' %self.sql_file )
        # if not os.path.exists(self.ans_file):
        #     raise MADlibSQLTestCaseException('ans file for this test case does not exist - %s' %self.ans_file )

        # pull out the intended docstring from the implied sql file
        # parent instantiation will conveniently look to that docstring to glean metadata
        intended_docstring = ""
        with open(self.sql_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.find('--') != 0:
                    break
                intended_docstring += line[2:].strip()
                intended_docstring += "\n"

        # this is the dynamic test function we will bind into the
        # generated test intance. (note the use of closures!)
        def implied_test_function(my_self):
            assert my_self._run_test(my_self.sql_file, my_self.ans_file)
        implied_test_function.__doc__ = intended_docstring
        method = new.instancemethod(implied_test_function,
                                    self,
                                    self.__class__)
        self.__dict__[methodName] = method
        
        super(MADlibSQLTestCase, self).__init__(methodName)

    # ----------------------------------------------------------------

    def _infer_metadata(self):
        super(MADlibSQLTestCase, self)._infer_metadata()
        self.db_name = self._metadata.get('db_name', self.db_name)
        self.username = self._metadata.get('username', None)
        if self._metadata.get('gucs', None) == None:
            self.gucs = set()
        else:
            self.gucs = set(self._metadata['gucs'].split(';'))

    # ----------------------------------------------------------------
            
    @classmethod
    def loadTestsFromTestCase(cls):
        tests = []
        source_file = sys.modules[cls.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))

        sql_dir = os.path.join(source_dir, cls.sql_dir)
        ans_dir = os.path.join(source_dir, cls.ans_dir)

        uniquePat = []
        for filename in os.listdir(sql_dir):
            if not fnmatch(filename, "*.sql"):
                continue
        
            sql_file = os.path.join(sql_dir, filename)
            partial_test_name = filename[:-4]
            ans_file = os.path.join(ans_dir, partial_test_name + ".ans")

            # if we don't find corresponding answer file,
            # just move on. it's probably used for something else.
            # if not os.path.exists(ans_file):
            #     os.system('touch %s' % (ans_file))
                # continue

            f = re.sub("_part\d+", "", partial_test_name)
            if f not in uniquePat:
                uniquePat.append(f)

        for pattern in uniquePat:
            # test_name = TINCTestLoader.testMethodPrefix + pattern
            test_name = pattern
            tests.append(cls(test_name))

        return tests

    # ----------------------------------------------------------------

    def get_source_dir(self):
        source_file = sys.modules[self.__class__.__module__].__file__
        source_dir = os.path.dirname(os.path.abspath(source_file))
        return source_dir

    # ----------------------------------------------------------------
    
    def get_sql_dir(self):
        return os.path.dirname(os.path.abspath(self.sql_file))

    # ----------------------------------------------------------------
        
    def get_ans_dir(self):
        return os.path.dirname(os.path.abspath(self.ans_file))

    # ----------------------------------------------------------------

    def get_out_dir(self):
        # If the sqls are located in a different directory than the source file, create an output
        # directory at the same level as the sql dir
        # if self.get_source_dir() == self.get_sql_dir():
        #     out_dir = os.path.join(self.get_sql_dir(),
        #                            self.__class__.out_dir)
        # else:
        #     out_dir = os.path.join(self.get_sql_dir(),
        #                            self.__class__.out_dir)
        out_dir = os.path.join(self.get_source_dir(),
                               self.__class__.out_dir)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        return out_dir

    # ----------------------------------------------------------------

    def setUp(self):
        """
        Run setup sql file if it exists
        """
        super(MADlibSQLTestCase, self).setUp()
        # Get the test case database class and run the database setup
        # which will be responsible for setting up the database for the test case
        # TODO - The TINCTestDatabase instance for the test case will be populated
        # in a global dict __databases__ in tinctest.databases.__databases__
        # which will be moved to a more appropriate location.
        if self.db_name is not None:
            __databases__[self.db_name].setUp()

        # Check if a common setup.sql file exists in the same location as the test sql
        setup_sql_file = os.path.join(os.path.dirname(os.path.abspath(self.sql_file)), 'setup.sql')
        if os.path.exists(setup_sql_file):
            tinctest.logger.info("Running setup sql for test - %s" %setup_sql_file)
            self._run_sql_file(setup_sql_file)

        # Check for test case specific sql file        
        test_case_setup_sql_file = self.sql_file.replace('.sql', '_setup.sql')
        if os.path.exists(test_case_setup_sql_file):
            tinctest.logger.info("Running setup sql for test - %s" %test_case_setup_sql_file)
            self._run_sql_file(test_case_setup_sql_file)

    # ----------------------------------------------------------------
        
    def tearDown(self):
        """
        Run teardown sql file if it exists
        """
        super(MADlibSQLTestCase, self).tearDown()
        # Check if a test case specific teardown sql exists
        teardown_sql_file = self.sql_file.replace('.sql', '_teardown.sql')
        if os.path.exists(teardown_sql_file):
            tinctest.logger.info("Running teardown sql for test - %s" %teardown_sql_file)
            self._run_sql_file(teardown_sql_file)

        # Check if a common teardown exists in the same location as the test sql
        teardown_sql_file = os.path.join(os.path.dirname(os.path.abspath(self.sql_file)), 'teardown.sql')
        if os.path.exists(teardown_sql_file):
            tinctest.logger.info("Running teardown sql for test - %s" %teardown_sql_file)
            self._run_sql_file(teardown_sql_file)

    # ----------------------------------------------------------------

    # MADlibTestCase will override this method
    def _run_test(self, sql_file, ans_file):
        """
        The method that subclasses should override to execute a sql test case differently.
        This encapsulates the execution mechanism of SQLTestCase. Given a base sql file and
        an ans file, runs all the sql files for the test case.

        Note that this also runs the other part sqls that make up the test case. For eg: if the
        base sql is query1.sql, the part sqls are of the form query1_part*.sql in the same location
        as the base sql.
        """
        self._gpdb_seg_log_file = sql_file.replace('.sql', '.segment_logs')
        guc_sql_file = self._add_gucs_to_sql_file(sql_file)
        if not self._run_sql_file(guc_sql_file, ans_file):
            return False
        
        # look for additional parts to run
        for parts in os.listdir(self.get_sql_dir()):
            part_sql_file = os.path.join(self.get_sql_dir(), parts)
            partial_test_name = sql_file.replace('.sql','')
            if not fnmatch(part_sql_file, partial_test_name+ "_part*.sql"):
                continue

            # Run the part sql
            part_ans_file = os.path.join(self.get_ans_dir(), os.path.basename(part_sql_file).replace('.sql', '.ans'))
            guc_sql_file = self._add_gucs_to_sql_file(part_sql_file)
            if not self._run_sql_file(guc_sql_file, part_ans_file):
                return False
        return True

    # ----------------------------------------------------------------

    def _add_gucs_to_sql_file(self, sql_file):
        """
        Form test sql file by adding the defined gucs to the sql file
        @param sql_file Path to  the test sql file
        @returns Path to the modified sql file
        """
        gucs_sql_file = os.path.join(self.get_out_dir(), os.path.basename(sql_file).replace('.sql', '_gucs.sql'))
        with open(gucs_sql_file, 'w') as o:
            gucs_write = (len(self.gucs) == 0)
            with open(sql_file, 'r') as f:
                for line in f:
                    if (line.find('--') != 0) and not gucs_write:
                        # Add gucs and then add the line
                        o.write('-- start_ignore\n')
                        for guc_string in self.gucs:
                            o.write("SET %s;" %guc_string)
                        gucs_write = True
                        o.write('\n-- end_ignore\n')
                        o.write(line)
                    else:
                        o.write(line)
        self.test_artifacts.append(gucs_sql_file)
        return gucs_sql_file

    # ----------------------------------------------------------------

    def _run_sql_file(self, sql_file, ans_file = None):
        """
        Given a sql file and an ans file, this adds the specified gucs (self.gucs) to the sql file , runs the sql
        against the test case databse (self.db_name) and verifies the output with the ans file.
        """
        result = True
        
        self.test_artifacts.append(sql_file)
        out_file = os.path.join(self.get_out_dir(), os.path.basename(sql_file).replace('.sql','.out'))
        self.test_artifacts.append(out_file)

        PSQL.run_sql_file(sql_file, dbname = self.db_name, out_file = out_file)

        if out_file[-2:] == '.t':
            out_file = out_file[:-2]
        
        if ans_file is not None:
            self.test_artifacts.append(ans_file)
            result = Gpdiff.are_files_equal(out_file, ans_file)
            if result == False:
                self.test_artifacts.append(out_file.replace('.out', '.diff'))

        return result

    # ----------------------------------------------------------------

    def collect_files(self):
        super(MADlibSQLTestCase, self).collect_files()

    # ----------------------------------------------------------------

    def defaultTestResult(self, stream=None, descriptions=None, verbosity=None):
        if stream and descriptions and verbosity:
            return MADlibSQLTestCaseResult(stream, descriptions, verbosity)
        else:
            return unittest.TestResult()

# ------------------------------------------------------------------------
            
class MADlibSQLTestCaseException(Exception):
    pass

# ------------------------------------------------------------------------

class MADlibSQLTestCaseResult(TINCTextTestResult):
    
    def __init__(self, stream, descriptions, verbosity):
        super(MADlibSQLTestCaseResult, self).__init__(stream, descriptions, verbosity)

    def addFailure(self, test, err):
        # Collect segment logs when a test fails
        segment_log_file = os.path.join(os.path.dirname(
            os.path.abspath(
                sys.modules[test.__class__.__module__].__file__)),
                                test._testMethodName[5:] + '.segment_logs')
        if not self.start_time:
            return

        # Guard against postmaster resets in a SQLTestCase in which case this will
        # throw an exception.
        try:
            with open(segment_log_file, "w") as file:
                array = GpArray.initFromCatalog(DbURL(), True)
                log_parts = collect_gpdb_logs(array, self.start_time, False)
                for part in log_parts:
                    file.write("-"*70)
                    file.write("\n  DBID %s (%s:%s)\n" % (part[0], part[1], part[2]))
                    file.write("-"*70)
                    file.write("\n%s" % part[3])
                    file.write("\n\n")
            test.test_artifacts.append(segment_log_file)
        except Exception, ex:
            tinctest.logger.warning("Exception while trying to collect gpdb logs - %s" %ex)
            
        super(MADlibSQLTestCaseResult, self).addFailure(test, err)


# class SQLPerformanceTestCase(SQLTestCase):

#     def __init__(self, methodName, sql_file=None, db_name = None):
#         self.repetitions = None
#         self.threshold = None
#         self.timeout = None
#         self._runtime = -1.0
#         self._plan_body = None # Add field to store plan body
#         self._avoid_execution = False; # Switch to control whether to avoid run test or not
#         super(SQLPerformanceTestCase, self).__init__(methodName, sql_file, db_name)
#         self.gucs.add('statement_timeout='+str(self.timeout))
        
#     def _infer_metadata(self):
#         super(SQLPerformanceTestCase, self)._infer_metadata()
#         self.repetitions = int(self._metadata.get('repetitions', '3'))
#         self.threshold = int(self._metadata.get('threshold', '5'))
#         self.timeout = int(self._metadata.get('timeout', '0'))  # 0 means unbounded by default.

#     def setUp(self):
#         # Setup the database by calling out to the super class
#         super(SQLPerformanceTestCase, self).setUp()
        
#         #Collect explain output and then compare with that of the last run
#         self._compare_previous_plan()
    
#     def _compare_previous_plan(self):
#         """
#         Get plan first and then compare with that of the previous run. If nothing change in the plan structure, 
#         there is no need to re-execute that query. The result will be copied from the previous run. 
#         """
#         #execute the explain sql to fetch plan
#         explain_sql_file = os.path.join(self.get_out_dir(), os.path.basename(self.sql_file).replace('.sql','_explain.sql'))
#         with open(explain_sql_file, 'w') as o:
#             with open(self.sql_file, 'r') as f:
#                 explain_write = False
#                 for line in f:
#                     if not line.startswith('--') and not explain_write:
#                         #keep all the GUCs
#                         o.write('-- start_ignore\n')
#                         for guc_string in self.gucs:
#                             o.write("SET %s;" %guc_string)
#                             o.write(line)
#                         o.write('-- end_ignore\n')
#                         o.write('explain %s' %line)
#                         explain_write = True
#                     else:
#                         o.write(line);
#         explain_out_file = os.path.join(self.get_out_dir(), os.path.basename(explain_sql_file).replace('.sql','.out'))
#         tinctest.logger.info("Gathering explain from sql : " + explain_sql_file)
#         PSQL.run_sql_file(explain_sql_file, dbname = self.db_name, out_file = explain_out_file)
#         # rewrite plan to keep plan body
#         self._rewrite_plan_file(explain_out_file)
        
#         # retrieve previous plan and store it into local file
#         if self.baseline_result:
#             if 'plan_body' in self.baseline_result.result_detail.keys():
#                 previous_explain_output = self.baseline_result.result_detail['plan_body']
#                 previous_explain_output_file = explain_out_file.replace('.out','_previous.out')
#                 with open(previous_explain_output_file, 'w') as o:
#                     o.write(previous_explain_output)
#                 # call GPDiff to compare two plans
#                 if Gpdiff.are_files_equal(previous_explain_output_file, explain_out_file):
#                     # two plans are the same, avoid execution
#                     self._avoid_execution = True
#                     self._runtime = self.baseline_result.value  # copy the runtime from previous result 
        
#     def _rewrite_plan_file(self, explain_out_file):
#         """
#         rewrite explain output to keep only GUC info and plan body
#         """
#         guc_plan_content = ''
#         with open(explain_out_file, 'r') as f:
#             able_to_write = True
#             for line in f:
#                 # ignore the part that from '-- end_ignore' to 'QUERY PLAN'
#                 if line.startswith('-- end_ignore'): 
#                     guc_plan_content += line
#                     able_to_write = False
#                 elif line.find('QUERY PLAN') != -1:
#                     guc_plan_content += '-- force_explain\n'
#                     able_to_write = True
#                 if able_to_write:
#                     guc_plan_content += line
#         self._plan_body = guc_plan_content
#         with open(explain_out_file, 'w') as o:
#             o.write(guc_plan_content)
        
#     def _run_test(self, sql_file, ans_file):
#         """
#         The method that subclasses should override to execute a sql test case differently.
#         This encapsulates the execution mechanism of SQLTestCase. Given a base sql file and
#         an ans file, runs all the sql files for the test case.

#         Note that this also runs the other part sqls that make up the test case. For eg: if the
#         base sql is query1.sql, the part sqls are of the form query1_part*.sql in the same location
#         as the base sql.
#         """
        
#         # if the plan is the same as previous one, skip this run
#         if self._avoid_execution:
#             str_runtime_list = []
#             for i in range(self.repetitions):
#                 str_runtime_list.append(str(self._runtime))
#             # dump statistics to a runtime_stats.csv file
#             output_file_path = os.path.join(self.get_out_dir(), 'runtime_stats.csv')
#             existing = os.path.exists(output_file_path)
#             mode = 'a' if existing else 'w'
#             with open(output_file_path, mode) as f:
#                 f.write("%s,%s\n" % (os.path.basename(sql_file), ",".join(str_runtime_list)))
#             return True
        
#         self._gpdb_seg_log_file = sql_file.replace('.sql', '.segment_logs')
#         guc_sql_file = self._add_gucs_to_sql_file(sql_file)
#         runtime_list = []
#         for i in range(self.repetitions):
#             runtime_list.append(self._run_and_measure_sql_file(guc_sql_file, i, ans_file))

#         # dump statistics to a runtime_stats.csv file
#         str_runtime_list = [str(x) for x in runtime_list]
#         output_file_path = os.path.join(self.get_out_dir(), 'runtime_stats.csv')
#         existing = os.path.exists(output_file_path)
#         mode = 'a' if existing else 'w'
#         with open(output_file_path, mode) as f:
#             f.write("%s,%s\n" % (os.path.basename(sql_file), ",".join(str_runtime_list)))

#         self._runtime = min(runtime_list)
#         return True

#     def _run_and_measure_sql_file(self, sql_file, iteration, ans_file = None):
#         """
#         Given a sql file and an ans file, this adds the specified gucs (self.gucs) to the sql file , runs the sql
#         against the test case databse (self.db_name) and verifies the output with the ans file.
#         """
#         result = True
        
#         self.test_artifacts.append(sql_file)
#         out_file = os.path.join(self.get_out_dir(), os.path.basename(sql_file).replace(".sql","_iter_%s.out" %iteration))
#         self.test_artifacts.append(out_file)

#         PSQL.run_sql_file(sql_file, dbname = self.db_name, out_file = out_file)

#         if ans_file is not None:
#             self.test_artifacts.append(ans_file)
#             result = Gpdiff.are_files_equal(out_file, ans_file)
#             if result == False:
#                 self.test_artifacts.append(out_file.replace('.out', '.diff'))
#                 self.fail('Diff failed between %s and %s' %(out_file, ans_file))

#         return self._get_runtime(out_file)

#     def _get_runtime(self, out_file):
#         """
#         Matches pattern <Time: 123.25 ms> and returns the sum of all the values found in the out file 
#         """
#         total_time = 0.0
#         with open(out_file, 'r') as f:
#             for line in f:
#                 if re.match('^Time: \d+\.\d+ ms', line):
#                     total_time += float(line.split()[1])
#         return total_time


#     def _add_gucs_to_sql_file(self, sql_file):
#         """
#         Form test sql file by adding the defined gucs to the sql file
#         @param sql_file Path to  the test sql file
#         @returns Path to the modified sql file
#         """
#         gucs_sql_file = os.path.join(self.get_out_dir(), os.path.basename(sql_file).replace('.sql', '_gucs.sql'))
#         with open(gucs_sql_file, 'w') as o:
#             gucs_write = False
#             with open(sql_file, 'r') as f:
#                 for line in f:
#                     if (line.find('--') != 0) and not gucs_write:
#                         o.write('-- start_ignore\n')
#                         o.write('\\timing\n')
#                         # Add gucs and then add the line
#                         for guc_string in self.gucs:
#                             o.write("SET %s;" %guc_string)
#                             o.write(line)
#                         gucs_write = True
#                         o.write('-- end_ignore\n')
#                     else:
#                         o.write(line)
#         self.test_artifacts.append(gucs_sql_file)
#         return gucs_sql_file

#     def defaultTestResult(self, stream=None, descriptions=None, verbosity=None):
#         if stream and descriptions and verbosity:
#             return SQLPerformanceTestCaseResult(stream, descriptions, verbosity)
#         else:
#             return unittest.TestResult()

# class SQLPerformanceTestCaseResult(TINCTextTestResult):

#     def __init__(self, stream, descriptions, verbosity):
#         super(SQLPerformanceTestCaseResult, self).__init__(stream, descriptions, verbosity)

#     def addSuccess(self, test):
#         # Add test._runtime to result.value
#         self.value = test._runtime
#         super(SQLPerformanceTestCaseResult, self).addSuccess(test)
#         # store the plan body into tincdb
#         self._store_plan_body(test) 

#     def addFailure(self, test, err):
#         """
#         Collect explain plan and an explain analyze output
#         """
#         self.value = test._runtime
#         super(SQLPerformanceTestCaseResult, self).addFailure(test, err)
#         # store the plan body into tincdb
#         self._store_plan_body(test)
        
#     def _store_plan_body(self, test):
#         self.result_detail['plan_body']=test._plan_body 

# class SQLConcurrencyTestCase(SQLTestCase, ConcurrencyTestCase):
#     """
# 	SQLConcurrencyTestCase consumes a SQL file, performs the psql on the same sql file using concurrent connections
#         specified by the 'concurrency' metadata.
#         Note the order of base classes in the above inheritance. With multiple inheritance, the order in which the base
#         class constructors will be called is from left to right. We first have to call SQLTestCase constructor which
#         will dynamically generate our test method which is a pre-requisite to call ConcurrencyTestCase.__init__ because
#         it works out of the test method that SQLTestCase generates. If you swap the order, good luck with debugging. 
#     """
#     def __init__(self, methodName):
#         super(SQLConcurrencyTestCase, self).__init__(methodName)

#     def _run_test(self, sql_file, ans_file):
#         # Construct an out_file name based on the currentime
#         # TODO - generate a more readable file name based 
#         # on the current execution context (using iteration and 
#         # thread id from ConcurrencyTestCase
#         now = datetime.datetime.now()
#         timestamp = '%s%s%s%s%s%s%s'%(now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond)
#         out_file = sql_file.replace('.sql', timestamp + '.out')
#         PSQL.run_sql_file(sql_file, dbname = self.db_name, out_file = out_file)

#         source_file = sys.modules[self.__class__.__module__].__file__
#         source_dir = os.path.dirname(source_file)
#         #look for additional parts to run
#         for parts in os.listdir(source_dir):
#             parts = os.path.join(source_dir, parts)
#             partial_test_name = sql_file.replace('.sql','')
#             if not fnmatch(parts, partial_test_name+ "_part*.sql"):
#                 continue
#             PSQL.run_sql_file(parts, dbname = self.db_name)
#             now = datetime.datetime.now()
#             timestamp = '%s%s%s%s%s%s%s'%(now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond)
#             out_file = parts.replace('.sql', timestamp + '.out')
#             if out_file[-2:] == '.t':
#                 out_file = out_file[:-2]
#             result = PSQL.run_sql_file(parts, dbname = self.db_name, out_file = out_file)
#             if result == False:
#                 return result
#         return True
