# convert sql data set to txt file that R can read
import re # regular expression
import sys

def convert (in_file, out_file):
    count = 0
    
    with open(out_file, "w") as of:
        for line in open(in_file):
            if line.startswith(("{", "array[")):
                size_x = 1 + len(re.findall(r",", line))
                count += 1
                elm = []
                x_count = 0
                for m in re.finditer(r"([^,\s\{\}]+)", line):
                    elm.append(m.group(1))
                if count == 1:
                    for i in range(1,size_x+1):
                        of.write("x" + str(i) + ",")
                    of.write("y")
                    for i in range(1,1 + len(elm) - size_x - 1):
                      of.write(",g%s" % i)
                    of.write("\n")
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

