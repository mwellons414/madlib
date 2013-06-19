
## @madlib-param dataset The data set name, string
## @madlib-param ans.path_ The answer file path

source("logregr_newapi_baseline.R")

## ------------------------------------------------------------------------
if(exists('dataset'))#Did we get any command line parameters?
{
	dataset <- as.character(dataset)
	ans.path_ <- as.character(ans.path_)
}else
{
	datasets <- c("patients_wi", "log_breast_cancer_wisconsin","log_wpbc")
	ans.path_ <- "../logregr_test.ans"

}
tincrepo <- Sys.getenv("TINCREPOHOME")
if(tincrepo == "")
{
	tincrepo <- "/Users/wellom1/tinc/tincrepo"
}


system(paste("rm ",ans.path_, sep = " "))#Get rid of the old file

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")


for (data.set in datasets) eval.logregr.append.results(data.set = data.set, sql.path=sql.path, outfileName = ans.path_)