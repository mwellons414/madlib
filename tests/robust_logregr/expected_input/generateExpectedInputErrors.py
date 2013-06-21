#!/usr/bin/python
## Generate the error messages for the input tests 


errorMessages = ['no error','invalid output table name given', 'maximum number of iterations must be positive',
"input table name does not exist.",
 "invalid name syntax",
 'column "badcolumnnamex" does not exist',  'invalid independent variable name given.' ,
'column "badcolumnnamey" does not exist', "invalid dependent variable name given." , 'no error', 'unknown optimizer requested','the tolerance cannot be negative' ]

for i in range(len(errorMessages)):
	ansFile = open("test_robust_logregr_input_"+str(i+1)+".ans","w")
	ansFile.write(errorMessages[i])
	ansFile.close()


