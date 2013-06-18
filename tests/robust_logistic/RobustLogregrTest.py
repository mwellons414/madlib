
## MADlib Tests for robust variance calculation of logistic regression

from madlib.src.template.madlib_test import MADlibTestCase
from madlib.src.test_utils.utils import unique_string
from madlib.src.test_utils.utils import string_to_array
from madlib.src.test_utils.utils import mean_squared_error
from madlib.src.test_utils.utils import read_sql_result
# from madlib.src.test_utils.get_dbsettings import get_schema_madlib
from madlib.src.test_utils.get_dbsettings import get_schema_testing
import os
import re
import sys
import math


def _generate_template_vars(arg_dict, default_arg_val):
	"""
	Args:
		@param argument_dict Dictionary (argument: [values for argument])
		@param default_arg_val Dictionary (argument: default value)

	Returns:
		List of dictionaries, each dictionary with single value for each argument
		and default values for the other arguments
	"""
	if not isinstance(arg_dict, dict):
		return arg_dict
	arg_dict_list = []	# list of argument dictionaries
	for each_arg_key, each_arg_vals in arg_dict.iteritems():
		for each_val in each_arg_vals:
			curr_arg_dict = dict((k,v) for k, v in default_arg_val.iteritems())
			curr_arg_dict[each_arg_key] = each_val
			arg_dict_list.append(curr_arg_dict)
	return arg_dict_list


# ------------------------------------------------------------------------

run_sql = """
		  set client_min_messages to error;
		  \\x on
		  select {schema_madlib}.robust_variance(
			  '{schema_testing}.{dataset}',
			  {tbl_outputInQuotes},
			  'logistic',
			  '{y}', '{x}');
		  select * from {tbl_output};
		  drop table if exists {tbl_output};
		  \\x off
		  """
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class RobustLogregrOutputTestCase (MADlibTestCase):
	"""
	Run templated SQL tests
	"""
	# ----------------------------------------------------------------
	# These class variable names are hard-coded and used by
	# template/madlib_test.py.
	# One should not change them
	# It is possible to make them un-hard-coded
	# But that does not seem to bring us much.
	# ----------------------------------------------------------------
	# Required by superclass
	ans_dir = "expected_output"

	# skip_file = "linregr_skip.py"
	
	template_method = "robust_logistic_output_test%{incr_}"

	template_doc = "This is for output tests of the robust covariance calculation of the logistic regression"

	template_vars = dict(
		# These names are not hard-coded
		tbl_output = unique_string(),
		dataset = ["patients_wi", "patients_bool_wi"],
		x = "x", 
		y = "y", 
		)
	template_vars['tbl_outputInQuotes']	 = "'" + template_vars['tbl_output'] + "'"

	template = run_sql

	# ----------------------------------------------------------------
	# The following class variables are defined only for this test
	# One can use any names here
	# ----------------------------------------------------------------
	# Since all R result is in one file
	# We just need to read it once
	r_resultfile = "robust_logregr_test.ans"
	Rresults = None

	#skip_file = "Robust_logregr_skip.py"

	# ----------------------------------------------------------------
	# One only needs to implement the result validation function
	def validate (self, sql_resultfile, answerfile):
		"""
		Compare the result of SQL with answer file
		Matching parameters in args
		"""
		sql_result = read_sql_result(sql_resultfile)
 
		# In this test, we use a single R result file, which
		# is source_dir/ans_dir/r_result. More parameters
		# are passed in by **args
		R_resultfile = os.path.join(self.get_source_dir(),
									self.get_ans_dir(),
									self.__class__.r_resultfile)

		# read the R result file only once
		# because all R results are in one file
		if self.__class__.Rresults is None:
			self.__class__.Rresults = self.read_Rresults(R_resultfile)

		args = sql_result["madlib_params"]
		dataset = args["dataset"].lower()
		r_coef = self.__class__.Rresults[dataset]["coef"]
		r_stdErr = self.__class__.Rresults[dataset]["stdErr"]
		r_tVal = self.__class__.Rresults[dataset]["tVal"]
		r_pVal = self.__class__.Rresults[dataset]["pVal"]

		(sql_coef, sql_stdErr, sql_tVal, sql_pVal) = self.get_coef(sql_result["result"])
		
		
		maxError = max( [mean_squared_error(sql_coef, r_coef), mean_squared_error(sql_stdErr, r_stdErr), mean_squared_error(sql_tVal, r_tVal), mean_squared_error(sql_pVal, r_pVal)])
		
		return maxError < 1e-6

	def get_coef (self, result):
		"""
		Extract the values from the SQL output
		"""
		coef = None
		stdErr = None
		tVal = None
		pVal = None
		for line in result:
			try:
				pattern = ".*?\{(.*?)\}"
				s = re.match("coef"+pattern, line)
				if(s != None):
					coef = map(float, string_to_array(s.group(1)))
					continue
			
				s = re.match("std_err"+pattern, line)
				if(s != None):
					stdErr = map(float, string_to_array(s.group(1)))
					continue
			
				s = re.match("t_stats"+pattern, line)
				if(s != None):
					#print s.group(1)
					tVal = map(float, string_to_array(s.group(1)))
					continue
				
				s = re.match("p_values" + pattern, line)
				if(s != None):
					#print s.group(1)
					pVal = map(float, string_to_array(s.group(1)))
					
			
			except:
				sys.exit("Robust Logregr Output Test Error: The array cannot be converted to float!")

		return (coef, stdErr, tVal, pVal)

	def read_Rresults (self, resultFile):
		"""
		Read R results from the answer file.
		Read only once for all the tests
		"""
		count = 0
		res = dict()
		with open(resultFile, "r") as f:
			for line in f:
				line = line.strip("\n").lower()
				count += 1
				if count == 1:
					#current_dataset = "'" + line + "'" 
					current_dataset = line 
					if current_dataset not in res.keys():
						res[current_dataset] = dict()
				elif count == 2:
					res[current_dataset]["coef"] = map(float, string_to_array(line))
				elif count == 3:
					res[current_dataset]["stdErr"] = map(float, string_to_array(line))
				elif count == 4:
					res[current_dataset]["tVal"] = map(float, string_to_array(line))
				elif count == 5:
					res[current_dataset]["pVal"] = map(float, string_to_array(line))
				elif line == "":
					count = 0 # reset count
		return res




# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class RobustLogregrInputTestCase (MADlibTestCase):
	"""
	Run input tests
	"""
	# ----------------------------------------------------------------
	# These class variable names are hard-coded and used by
	# template/madlib_test.py.
	# One should not change them
	# It is possible to make them un-hard-coded
	# But that does not seem to bring us much.
	# ----------------------------------------------------------------
	ans_dir = "expected_input" if MADlibTestCase.dbKind() == "greenplum" \
			  else "expect_input_pg"


	template_method = "robust_logregr_input_test_{incr_}"
	template_doc = "This is for input tests of the robust covariance calculation of the logistic regression"
	
	outTable = unique_string()
	argument_dict = dict(
		# These names are not hard-coded
		tbl_output = [],
		tbl_outputInQuotes = ["NULL"],
		dataset = ["nonExistentTable"],
		x = ["BadColumnNameX"],
		y = ["BadColumnNameY"]
		)
	argument_defaults = dict(
		# These names are not hard-coded
		tbl_output = outTable,
		dataset = ["patients_wi"],
		x = "x",
		y = "y"
		)
	argument_defaults["tbl_outputInQuotes"] = "'"+argument_defaults["tbl_output"] +"'"
	
	template_vars = _generate_template_vars(argument_dict, argument_defaults)	 
	template = run_sql

	 # One only needs to implement the result validation function
	def validate (self, sql_resultfile, answerfile):
		"""
		Compare the result of SQL with answer file
		Matching parameters in args
		"""
		sql_result = read_sql_result(sql_resultfile)

		args = sql_result["madlib_params"]
		
		errMessage = self.get_errMessage(sql_result["result"])
		#print sql_result["result"]
		
		#print "Error message"
		#print errMessage
		expectedResults = self.get_expectedInput(answerfile)
	
		#print "Expected Input"
		#print expectedResults
		return errMessage == expectedResults


	#skip_file = "Robust_logregr_skip.py"
 

	def get_expectedInput (self, resultFile):
		#Get the expected results
		count = 0
		res = dict()
		with open(resultFile, "r") as f:
			for line in f:
				line = line.strip("\n")
				return line
				

	def get_errMessage (self, result):
		#Extract the values from the SQL output
		message = None
		for line in result:
			#print line
			pattern = ".*ERROR:\s*(.*)"
			s = re.match(pattern, line)
			#print s
			if(s != None):
				message = s.group(1)
				
				break

		return message
