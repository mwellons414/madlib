# convert sql data set to txt file that R can read
import re # regular expression
import sys

def convert (in_file, out_file):
	count = 0
	
	numCols = None
	with open(out_file, "w") as of:
		for line in open(in_file):
		
			#Check if this has two columns or more than two columns
			if line.startswith(("{", "array[")) and numCols == None:
				tokens = line.split("\t")
				numCols = len(tokens)
				
					
			
		
			if line.startswith(("{", "array[")) and numCols==2:
				count += 1
				elm = []
				for m in re.finditer(r"([^,\s\{\}]+)", line):
					elm.append(m.group(1))
				if count == 1:
					for i in range(len(elm)-1):
						of.write("x" + str(i+1) + ",")
					of.write("y\n")
				for i in range(len(elm)):
					if(elm[i].lower() == "t" or elm[i].lower() == "true"):
						elm[i] = "1"
					if(elm[i].lower() == "f" or elm[i].lower() == "false"):
						elm[i] = "0"
					of.write(elm[i])
					if i != len(elm) - 1:
						of.write(",")
					else:
						of.write("\n")

			if line.startswith(("{", "array[")) and numCols==3:
				count += 1
				elm = []
				for m in re.finditer(r"([^,\s\{\}]+)", line):
					elm.append(m.group(1))
				if count == 1:
					for i in range(len(elm)-2):
						of.write("x" + str(i+1) + ",")
					of.write("y,")
					of.write("z\n")
				for i in range(len(elm)):
					if(elm[i].lower() == "t" or elm[i].lower() == "true"):
						elm[i] = "1"
					if(elm[i].lower() == "f" or elm[i].lower() == "false"):
						elm[i] = "0"
					of.write(elm[i])
					if i != len(elm) - 1:
						of.write(",")
					else:
						of.write("\n")

if __name__ == "__main__":
	convert (sys.argv[1], sys.argv[2])
	# convert('../data/log_breast_cancer_wisconsin.sql', '../data/test.txt')

