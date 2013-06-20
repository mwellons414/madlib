#!/usr/bin/python
## Generate the error messages for the input tests 


errorMessages = ['column "badcolumnnamey" does not exist', "invalid dependent variable name given.", "no error", 'column "badcolumnnamex" does not exist', 'invalid independent variable name given.', 'invalid output table name given', "input table name does not exist.", "invalid name syntax"]

for i in range(len(errorMessages)):
	ansFile = open("test_robust_logregr_input_"+str(i+1)+".ans","w")
	ansFile.write(errorMessages[i])
	ansFile.close()


