
## @madlib-param dataset The data set name, string
## @madlib-param ans.path_ The answer file path

source("logregr_newapi_baseline.R")

## ------------------------------------------------------------------------
if(exists('dataset'))#Did we get any command line parameters?
{
	data.path = paste(ans.path_, "/data/", sep = "")
	ans.path_ <- as.character(ans.path_)
}else
{
	datasets <- c("log_ornstein_wi")
	ans.path_ <- "../logregr_group_test.ans"
}

system(paste("rm ",ans.path_, sep = " "))#Get rid of the old file

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")

eval.logregr.append.results(data.set = datasets,
                             target = "y",
                             predictors = "~ . -1 - z",
                             grouping.cols = c("z"),
                             sql.path='~/madlib_testsuite/datasets/sql', outfileName = ans.path_)
