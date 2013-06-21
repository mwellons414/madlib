
## @madlib-param dataset The data set name, string
## @madlib-param incr_ The count of the test cases, when _incr is 1, create the answer file
## @madlib-param ans.path_ The answer file path

source("logregr_newapi_baseline.R")

## ------------------------------------------------------------------------
if(exists('datasets'))#Did we get any command line parameters?
{
	datasets <- as.character(datasets)
	ans.path_ <- as.character(ans.path_)
	resultFile <- paste(ans.path_, "/logregr_test.ans", sep="")
	if (incr_ == 1) system(paste("rm -f", resultFile))
}else #Use the default settings
{
	datasets <- c("patients_wi", "log_breast_cancer_wisconsin","log_wpbc")
	resultFile <- "../logregr_test.ans"
	system(paste("rm ",resultFile, sep = " "))#Get rid of the old file

}
tincrepo <- Sys.getenv("TINCREPOHOME")
if(tincrepo == "")
{
	tincrepo <- "~/tinc/tincrepo/"
}

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")


for (data.set in datasets) eval.logregr.append.results(data.set = data.set, sql.path=sql.path, outfileName = resultFile)

rm(datasets)
