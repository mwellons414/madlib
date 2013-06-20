
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

#Check the relative error between the r and sql values.  Returns true if all the entries match to within the error tolerance
def checkEntries(r_values, sql_values, errorTol = 1e-2):
	
	#Return true if the entries are within the specified tolerance
	def rel_err(r, sql, errorTol):	
		if(r == 0):
			return abs(r - sql) < errorTol
		else:
			return abs( (r - sql)/r) < errorTol
	
	if(type(r_values) != type([]) and type(r_values) != type( (0,0) )):
		return rel_err(r_values, sql_values, errorTol) #if the r_values and  sql values are a singleton

	if(len(r_values) !=  len(sql_values) ): #Make sure the list of r values and sql values have the same number of entries
		return False
	
	for i in range(len(r_values)):
		if( not rel_err(r_values[i], sql_values[i],  errorTol) ):
			return False
	return True


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
		  \\x on
		  set client_min_messages to error;
		  select {schema_madlib}.logregr_train(
			  '{schema_testing}.{dataset}',
			  {tbl_outputInQuotes},
			  '{y}', '{x}', {grouping_col}, {max_iteration}, '{optimizer}', '{convergence_threshold}');
		  select * from {tbl_output};
		  drop table if exists {tbl_output};
		  \\x off
		  """
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class LogregrOutputTestCase (MADlibTestCase):
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
	
	template_method = "logistic_output%{incr_}"

	template_doc = "This is for output tests of the the logistic regression"

	template_vars = dict(
		# These names are not hard-coded
		tbl_output = unique_string(),
		dataset = ["patients_wi", "log_breast_cancer_wisconsin","log_wpbc"],
		x = "x", 
		y = "y", 
		grouping_col = "NULL::VARCHAR",
		max_iteration = "20",
		optimizer = 'irls',
		convergence_threshold = 0.00001
		)
	template_vars['tbl_outputInQuotes']	 = "'" + template_vars['tbl_output'] + "'"

	template = run_sql

	# ----------------------------------------------------------------
	# The following class variables are defined only for this test
	# One can use any names here
	# ----------------------------------------------------------------
	# Since all R result is in one file
	# We just need to read it once
	r_resultfile = "logregr_test.ans"
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
	
		#print(sql_result)

		args = sql_result["madlib_params"]
		dataset = args["dataset"].lower()
		r_coef = self.__class__.Rresults[dataset]["coef"]
		r_stdErr = self.__class__.Rresults[dataset]["stdErr"]
		r_tVal = self.__class__.Rresults[dataset]["tVal"]
		r_pVal = self.__class__.Rresults[dataset]["pVal"]
		r_odds = self.__class__.Rresults[dataset]["odds_ratios"]
		r_ll = self.__class__.Rresults[dataset]["log_likelihood"]
		r_conNum = self.__class__.Rresults[dataset]["condition_number"]

		(sql_coef, sql_stdErr, sql_tVal, sql_pVal, sql_odds, sql_ll, sql_conNum) = self.get_sqlResult(sql_result["result"])
		
		allTestPassed = True
		debug = False
		if(debug):
			print "Comparing coefficients"
		if(not checkEntries(sql_coef, r_coef)):
			print checkEntries(sql_coef, r_coef)
			for i in range(len(sql_coef)):
				print i, sql_coef[i], r_coef[i], sql_coef[i] - r_coef[i]
			print "Coefficients don't match"
			allTestPassed= False
		
		if(debug):
			print "Comparing Standard Errors"
		if(not checkEntries(sql_stdErr, r_stdErr) ):
			for i in range(len(sql_stdErr)):
				if( abs(sql_stdErr[i] - r_stdErr[i]) > 1e-6):
					print i, sql_stdErr[i], r_stdErr[i]
			print "Standard errors don't match"
			allTestPassed= False
		
		if(debug):
			print "Comparing Wald statistics"
		if(not checkEntries(sql_tVal, r_tVal)):
			print "Wald statistics don't match"
			allTestPassed= False
		
		if(debug):
			print "Comparing p-values"
		if(not checkEntries(sql_pVal, r_pVal)):
			print "P-values don't match"
			for i in range(len(sql_stdErr)):
				print i, sql_stdErr[i], r_stdErr[i], sql_stdErr[i] - r_stdErr[i]
			allTestPassed= False
		
		if(debug):
			print "Comparing odds ratios"
			for i in range(len(sql_odds)):
				print i, sql_odds[i], r_odds[i],sql_odds[i] - r_odds[i]
		if(not checkEntries(sql_odds, r_odds)):
			print "Odds ratios don't match"
			allTestPassed= False
		
		if(debug):
			print "Comparing log likelyhood"	
		if(not checkEntries(sql_ll , r_ll)):
			print "Log likelyhood doesn't match"
			allTestPassed= False
		
		if(not checkEntries(sql_conNum , r_conNum)):
			print "Condition number doesn't match"
			allTestPassed= False
		
		return allTestPassed

	def get_sqlResult (self, result):
		"""
		Extract the values from the SQL output
		"""
		coef = None
		stdErr = None
		tVal = None
		pVal = None
		oddsRatio = None
		logLike = None
		conditionNum = None
		for line in result:
			#print line
			#Deal with Nulls
			try:
				pattern = ".*?\{(.*?)\}"
				
				s = re.match("coef"+pattern, line)
				if(s != None):
					#print "coef"
					coef = map(float, string_to_array(s.group(1)))
					continue
			
				s = re.match("std_err"+pattern, line)
				if(s != None):
					#print "std_err"
					stdErr = map(float, string_to_array(s.group(1)))
					continue
			
				s = re.match("z_stats"+pattern, line)
				if(s != None):
					#print "z_stats"
					#print s.group(1)
					tVal = map(float, string_to_array(s.group(1)))
					continue
				
				s = re.match("p_values" + pattern, line)
				if(s != None):
					#print s.group(1)
					pVal = map(float, string_to_array(s.group(1)))
					
				s = re.match("odds_ratios" + pattern, line)
				if(s != None):
					oddsRatio = map(float, string_to_array(s.group(1)))
				
				s = re.match("log_likelihood.*?\|(.*)", line)
				if(s != None):
					logLike = float(s.group(1))
					
				s = re.match("condition_no.*?\|(.*)", line)
				if(s != None):
					conNum = float(s.group(1))
			
			except:
				sys.exit("Logregr Output Test Error: The array cannot be converted to float!")

		return (coef, stdErr, tVal, pVal, oddsRatio, logLike, conNum)

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
				line = line.replace("null", "NaN")
				#print line

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
				elif count == 6:
					res[current_dataset]["log_likelihood"] = float(line)
				elif count == 7:
					res[current_dataset]["odds_ratios"] = map(float, string_to_array(line))
				elif count == 8:
					res[current_dataset]["condition_number"] = float(line)
				elif line == "":
					count = 0 # reset count
		return res



class LogregrOutputTestCase2 (MADlibTestCase):
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
	
	template_method = "logistic_output_group%{incr_}"

	template_doc = "This is for output tests of the the logistic regression with grouping"

	template_vars = dict(
		# These names are not hard-coded
		tbl_output = unique_string(),
		dataset = ["log_ornstein_wi", ],
		x = "x", 
		y = "y", 
		grouping_col = "'z'",
		max_iteration = "20",
		optimizer = 'irls',
		convergence_threshold = 0.00001
		)
	template_vars['tbl_outputInQuotes']	 = "'" + template_vars['tbl_output'] + "'"

	template = run_sql

	# ----------------------------------------------------------------
	# The following class variables are defined only for this test
	# One can use any names here
	# ----------------------------------------------------------------
	# Since all R result is in one file
	# We just need to read it once
	r_resultfile = "logregr_group_test.ans"
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
	
		#print(self.__class__.Rresults)

		args = sql_result["madlib_params"]
		dataset = args["dataset"].lower()
		self.__class__.SQLresults = self.get_sqlResult(sql_result["result"])

		groups = self.__class__.Rresults[dataset].keys()
		print groups
		print self.__class__.Rresults
		print self.__class__.SQLresults
		allTestPassed = True
		debug = False

		#print self.__class__.sql_results
		#print self.__class__.Rresults
			
		for group in groups:
			for key in self.__class__.SQLresults[group].keys():
				#print dataset, group, key
				if(not checkEntries(self.__class__.SQLresults[group][key], self.__class__.Rresults[dataset][group][key])):
					print "Mismatch in the values of", key, "for group", group
					allTestPassed= False
		
		
		return allTestPassed

	def get_sqlResult (self, result):
		"""
		Extract the values from the SQL output
		"""
		
		sql_values = dict()
		group = None
		for line in result:
		
			pattern = "^z\s+\|\s*([0-9]+)"
			#pattern = "(.*)"
			s = re.match(pattern, line)#, re.IGNORECASE)
			if(s != None):
				#print s, line, s.group(1)
				group = s.group(1)
				sql_values[group] = {}
			elif(group == None):
				continue
			#print line
			#Deal with Nulls
			try:
				pattern = ".*?\{(.*?)\}"
				keywordsArray = ["coef","std_err","z_stats","p_values","odds_ratios" ]
				keywordsSingle = ["log_likelihood", "condition_no"]
				
				for keyword in keywordsArray:
					s = re.match(keyword+pattern, line)
					if(s != None):
						sql_values[group][keyword] = map(float, string_to_array(s.group(1)))
						continue
				
				for keyword in keywordsSingle:
					s = re.match(keyword+".*?\|(.*)", line)
					if(s != None):
						sql_values[group][keyword] = float(s.group(1))
						continue
				
			
			except:
				print "Unexpected error:", sys.exc_info()[0]
				sys.exit("Error in LogregrOutputTestCase2")

		return sql_values

	def read_Rresults (self, resultFile):
		"""
		Read R results from the answer file.
		Read only once for all the tests
		"""
		count = 0
		res = dict()
		with open(resultFile, "r") as f:
			group = 1
			for line in f:
				line = line.strip("\n").lower()
				line = line.replace("null", "NaN")
				#print line

				count += 1
				if(re.match("^[a-zA-Z]",line)):
					count = 0
					#current_dataset = "'" + line + "'" 
					current_dataset = line 
					if current_dataset not in res.keys():
						res[current_dataset] = dict()
				elif count == 1:
					group = line.strip('"')
					res[current_dataset][group] = dict()
				elif count == 2:
					res[current_dataset][group]["coef"] = map(float, string_to_array(line))
				elif count == 3:
					res[current_dataset][group]["std_err"] = map(float, string_to_array(line))
				elif count == 4:
					res[current_dataset][group]["z_stats"] = map(float, string_to_array(line))
				elif count == 5:
					res[current_dataset][group]["p_values"] = map(float, string_to_array(line))
				elif count == 6:
					res[current_dataset][group]["log_likelihood"] = float(line)
				elif count == 7:
					res[current_dataset][group]["odds_ratios"] = map(float, string_to_array(line))
				elif count == 8:
					res[current_dataset][group]["condition_no"] = float(line)
				elif line == "":
					count = 0
		return res


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

class LogregrInputTestCase (MADlibTestCase):
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


	template_method = "logregr_input_{incr_}"
	template_doc = "This is for input tests of the robust covariance calculation of the logistic regression"
	
	outTable = unique_string()
	argument_dict = dict(
		# These names are not hard-coded
		tbl_output = [],
		tbl_outputInQuotes = [],
		dataset = ["non_existing_source_table"],
		x = ["non_existing_dependent_varname"],
		y = ["non_existing_independent_varname"],
		max_iteration = ["-1"],
		optimizer = ['invalid_optimizer'],
		convergence_threshold = [-0.0001],
		)
	argument_defaults = dict(
		# These names are not hard-coded
		tbl_output = outTable,
		dataset = ["patients_wi"],
		x = "x",
		y = "y",
		max_iteration = "20",
		optimizer = 'irls',
		convergence_threshold = 0.00001,
		grouping_col = "NULL::VARCHAR"
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
		return expectedResults in errMessage 


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
			pattern = ".*ERROR:\s*(\w.*?)\("
			s = re.match(pattern, line)
			if(s != None):
				message = s.group(1)
				break

		return message
