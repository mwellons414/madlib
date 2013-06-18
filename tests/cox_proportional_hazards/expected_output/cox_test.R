## ------------------------------------------------------------------------
## Generate R results for validation
##
## The parameter values are fed from TINC
##
## Put all the results into one file
##
## This is a quite general example, which does not support grouping
## ------------------------------------------------------------------------

## @madlib-param dataset The data set name, string
## @madlib-param incr_ The count of the test cases, when _incr is 1, create the answer file
## @madlib-param ans.path_ The answer file path


# fit1 <- coxph(Surv(y, status) ~ x, data=Rossi)
display_dataset <- as.character(dataset)
dataset <- as.character(dataset)

## ------------------------------------------------------------------------

## Other parameters
target <- "y"                  # dependent variable
predictors <- " ~ . "        # fitting formula
status <- " status "        # fitting formula
survival_formula = paste('Surv(', target, ',', status, ')')
## ------------------------------------------------------------------------

tincrepo <- Sys.getenv("TINCREPOHOME")

suppressMessages(library(lmtest))
suppressMessages(library(survival))
suppressMessages(library(car))
source(paste(tincrepo, "/madlib/src/r_utils/utils.R", sep = ""))

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")
data.path = paste(ans.path_, "/data/", sep = "")
system(paste("rm -rf", data.path))
system(paste("mkdir", data.path))
py.path = paste(tincrepo, "/madlib/src/r_utils", sep = "")
result.file <- paste(ans.path_, "/cox_prop_hazards.ans", sep = "")
if (incr_ == 1) system(paste("rm -f", result.file))

## ------------------------------------------------------------------------
con <- file(result.file, "a")
name <- dataset
dat <- prepare_cox.dataset(name, sql.path = sql.path,
                        data.path = data.path,
                        py.path = py.path)

print(py.path)
print(sql.path)
print(data.path)
## The independent variable columns
n <- length(names(dat))-2
print(dat)

## Actual computation part
fit <- coxph(formula(paste(survival_formula, predictors),ties="breslow"), data = dat)
fit.sum <- summary(fit)
l <- length(fit$coefficients)
##
cat(paste(display_dataset, "\n", sep = ""), file = con)
output.vec(fit.sum$coefficients[1:l,1], con) # coef
output.vec(fit.sum$coefficients[1:l,3], con) # std err
output.vec(fit.sum$coefficients[1:l,4], con) # t value
output.vec(fit.sum$coefficients[1:l,5], con) # p value
cat("\n", file = con)
close(con)
