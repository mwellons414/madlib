source("./utils/utils.r")
## @madlib-param datasets The data set name, string
## @madlib-param incr_ The count of the test cases, when _incr is 1, create the answer file
## @madlib-param ans.path_ The answer file path

source("logregr_newapi_baseline.R")
tincrepo <- Sys.getenv("TINCREPOHOME")
if(tincrepo == "")
{
	tincrepo <- "~/tinc/tincrepo/" #If the tincrepo isn't set.  Make a guess about where it is.  
}

## ------------------------------------------------------------------------
if(exists('datasets'))#Did we get any command line parameters?
{
	datasets <- as.character(datasets)
	ans.path_ <- as.character(ans.path_)
}else
{
	datasets <- c("log_ornstein_wi")
	ans.path_ <- "../logregr_group_test.ans"
}

system(paste("rm ",ans.path_, sep = " "))#Get rid of the old file

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")
for( i in seq_along(datasets))
{
	dataset <- datasets[i]
	eval.logregr.append.results(data.set = dataset,
                             target = "y",
                             predictors = "~ . -1 - z",
                             grouping.cols = c("z"),
                             sql.path='~/madlib_testsuite/datasets/sql', outfileName = ans.path_)
}
rm(datasets)
