#!/usr/bin/python
## Generate the error messages for the input tests 


errorMessages = ["The tolerance cannot be negative!", "Data table does not exist!", "no error", "Grouping column does not exist","non_existing_dependent_varname", "non_existing_independent_varname", "Unknown optimizer requested", "Maximum number of iterations must be positive!"]

for i in range(len(errorMessages)):
	ansFile = open("test_logregr_input_"+str(i+1)+".ans","w")
	ansFile.write(errorMessages[i])
	ansFile.close()


