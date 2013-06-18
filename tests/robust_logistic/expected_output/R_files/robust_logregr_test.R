
## -----------------------------------------------------------------------
## Generate R results for validation
## -----------------------------------------------------------------------

library(lmtest)
library(car)
library(sandwich)

source("~/madlib_testsuite/src/r_utils/utils.R")

## robust logistic regression R result
hsd.append.results <- function(datasets, 
                               sql.path = "~/madlib_testsuite/datasets/sql/",
                               data.path = "~/temp/", 
                               py.path = "~/madlib_testsuite/src/r_utils"
                               , firstTest = TRUE)
{
	if(firstTest == TRUE)
	{
		writeMode = "w"
	}
	else
	{
		writeMode = "a"
	}
    con <- file("robust_Logregr_test.ans", writeMode)
    for (i in seq_along(datasets))
    {
        name <- datasets[i]
        
        dat <- prepare.dataset(name, sql.path = sql.path, data.path = data.path, py.path = py.path)
        lastTwoDigits = substr(name, nchar(name)-1,nchar(name))
        if(lastTwoDigits == "oi")
        {
			substr(name, nchar(name)-1,nchar(name)) <- "wi"
        }
        print(name)
        #print(dat)
        if (! is.null(dat))
        {
            if (sum(is.na(dat)) > 0) next
            ##
            regress <- glm( y ~ . , family=binomial("logit"), data = dat)
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

datasets <- c("patients_oi", "patients_bool_oi")

hsd.append.results(datasets, firstTest = TRUE);
#hsd.append.results(datasets, firstTest = FALSE);

