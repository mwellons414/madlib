
## ------------------------------------------------------------------------
## Generate R results for validation
##
## The parameter values are fed from TINC
##
## Put all the results into one file
## ------------------------------------------------------------------------

## @madlib-param dataset The data set name, string
## @madlib-param hetero The heteroskedasticity flag, boolean
## @madlib-param incr_ The count of the test cases, when _incr is 1, create the answer file
## @madlib-param ans.path_ The answer file path

dataset <- as.character(dataset)
hetero <- as.logical(toupper(hetero))

library(lmtest)
library(car)
source("/Users/qianh1/workspace/madlib_testsuite/src/r_utils/utils.R")

sql.path = "~/workspace/testsuite/dataset/sql/"
data.path = "/Users/qianh1/workspace/madlib_testsuite/examples/linregr_expected/data/"
py.path = "/Users/qianh1/workspace/madlib_testsuite/src/r_utils"

result.file <- paste(ans.path_, "/linregr_test2.ans", sep = "")

if (incr_ == 1) system(paste("rm -f", result.file))

con <- file(result.file, "a")
name <- dataset
dat <- prepare.dataset(name, sql.path = sql.path,
                        data.path = data.path,
                        py.path = py.path)
if (! is.null(dat))
{
    if (sum(is.na(dat)) > 0) next
    ##
    fit <- lm(y ~ . - 1, data = dat)
    fit.sum <- summary(fit)
    l <- length(fit$coefficients)
    if (hetero) {
        ## bp <- bptest(fit)
        ## cf <- coeftest(fit, vcov = hccm(fit, type = "hc0"))
        bp <- list(statistic = 0, p.value = 0.9)
        cf <- rep(0, 4*l)
    } 
    kp <- kappa(fit, exact = TRUE)
    ##
    cat(paste(name, "\n", sep = ""), file = con)
    cat(paste(as.character(hetero), "\n", sep = ""), file = con)
    output.vec(fit$coefficients, con) # coef
    cat(paste(fit.sum$r.square, "\n", sep = ""), file = con) # coef
    output.vec(fit.sum$coefficients[(1:l) + l], con) # std err
    output.vec(fit.sum$coefficients[(1:l) + 2*l], con) # t value
    output.vec(fit.sum$coefficients[(1:l) + 3*l], con) # p value
    cat(paste(kp, "\n", sep = ""), file = con) # condition number
    if (hetero) {
        cat(paste(bp$statistic, "\n", sep = ""), file = con)
        cat(paste(bp$p.value, "\n", sep = ""), file = con)
        ## output.vec(cf[(1:l) + l], "double precision[]", ",\n", con)
        ## output.vec(cf[(1:l) + 2*l], "double precision[]", ",\n",  con)
        ## output.vec(cf[(1:l) + 3*l], "double precision[]", ");\n\n",  con)
    }
    cat("\n", file = con)
}
close(con)
