## @madlib-param dataset The data set name, string
## @madlib-param incr_ The count of the test cases, when incr_ is 1, create the answer file
## @madlib-param ans.path_ The answer file path
## -----------------------------------------------------------------------
## Generate R results for validation
## -----------------------------------------------------------------------

library(lmtest)
library(car)
library(sandwich)

tincrepo <- Sys.getenv("TINCREPOHOME")
if(tincrepo == "")
{
	tincrepo <- "~/tinc/tincrepo/" #If the tincrepo isn't set.  Make a guess about where it is.  
}

if(exists('dataset'))#Did we get any command line parameters?
{
	dataset <- as.character(dataset)
	ans.path_ <- as.character(ans.path_)
	resultFile <- paste(ans.path_, "/robust_logregr_test.ans", sep="")
	if (incr_ == 1) system(paste("rm -f", resultFile))
}else
{
	dataset <- c("patients_wi", "patients_bool_wi", "log_breast_cancer_wisconsin", "log_wpbc")
	resultFile <- "robust_logregr_test.ans"
	system(paste("rm -f", resultFile))
}

#system(paste("rm ",ans.path_, sep = " "))#Get rid of the old file
sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")
py.path = paste(tincrepo, "/madlib/src/r_utils/", sep = "")

source( paste(py.path, "utils.R", sep = "")) #grab the R utilities script

## robust logistic regression R result
hsd.append.results <- function(datasets, 
                               sql.path = "~/madlib_testsuite/datasets/sql/",
                               data.path = "./temp/", 
                               py.path = "~/madlib_testsuite/src/r_utils",
                               outputPath = "../robust_Logregr_test.ans")
{
	con <- file(outputPath, "a")
    for (i in seq_along(datasets))
    {
        name <- datasets[i]
        
        dat <- prepare.dataset(name, sql.path = sql.path, data.path = data.path, py.path = py.path)
        
        #print(name)
        #print(dat)
        if (! is.null(dat))
        {
            if (sum(is.na(dat)) > 0) next
            ##
            regress <- glm( y ~ . -1 , family=binomial("logit"), data = dat)
            cat(paste(name, "\n", sep = ""), file = con)
            otherStats  = coeftest(regress, vcov = vcovHC(regress, type = "HC0"))
            l <- length(regress$coefficients)
            coeff = otherStats[1:l,1] #Regression coefficients
            stdErr = otherStats[1:l,2] #Std. Error
            tVal = otherStats[1:l,3] # The t-stats/z-stats
            pVal = otherStats[1:l,4] #The p-values
            output.vec(coeff, con)
            output.vec(stdErr, con)
            output.vec(tVal, con)
            output.vec(pVal, con)
            cat("\n", file = con)
            
        }
    }
    close(con)
}

## ------------------------------------------------------------------------

hsd.append.results(dataset, sql.path = sql.path, py.path = py.path, outputPath =resultFile);
rm(dataset)

