
## ------------------------------------------------------------------------
## Generate R results for validation
##
## The parameter values are fed from TINC
##
## Put all the results into one file
##
## This is a quite general example, which also supports grouping
## ------------------------------------------------------------------------

## @madlib-param dataset The data set name, string
## @madlib-param method.name_ The answer file path
## @madlib-param ans.path_ The answer file path

dataset <- as.character(dataset)
method.prefix = sub(".sql", "", method.name_)

## ------------------------------------------------------------------------

## Other parameters
target <- "y"                  # dependent variable
predictors <- "~ . - 1"        # fitting formula
grouping.cols <- character(0)  # grouping column name VECTOR
not.xcols <- grouping.cols     # exclude these columns

## ------------------------------------------------------------------------

tincrepo <- Sys.getenv("TINCREPOHOME")

suppressMessages(library(nnet))
source(paste(tincrepo, "/madlib/src/r_utils/utils.R", sep = ""))

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")
data.path = paste(ans.path_, "/data/", sep = "")
system(paste("rm -rf", data.path))
system(paste("mkdir", data.path))
py.path = paste(ans.path_, "/R_files", sep = "")

result.file <- paste(ans.path_, "/", method.prefix, ".ans", sep = "")
## ------------------------------------------------------------------------

con <- file(result.file, "w")

name <- dataset
dat <- prepare.dataset(name, sql.path = sql.path,
                        data.path = data.path,
                        py.path = py.path)

## The independent variable columns
xcols <- setdiff(names(dat), c(target, not.xcols))
n <- length(xcols)
grouping.str <- paste("\"", grouping.cols, "\"", collapse = ", ", sep = "")

##
if (length(grouping.cols) != 0) {
    ## grouping the original data
    grps <- by(dat, dat[grouping.cols], rbind)
    ## extract grouping column values
    cats <- attr(grps, "dimnames")
    ## for each combination of grouping column values, form a string
    grouping.vals <- str.combine(cats) 
} else {
    grps <- list(dat = dat)
    grouping.vals <- ""
}
## 
for (gval in grouping.vals)
{
    ## extract the data for a specific combination of grouping column values
    dat.use <- eval(parse(text = paste("grps[", gval, "][[1]]", sep = "")))
    ## ----------------------------------------------------------------

    fit <- multinom(formula(paste(target, predictors)), data = dat.use)
    fit.sum <- summary(fit)

    cat("coef   |", file = con)
    output.vec(fit.sum$coefficients, con) 

    cat("std_err    |", file = con)
    output.vec(fit.sum$standard.errors, con)

    cat("log_likelihood |", file = con)
    output.vec(-fit.sum$value, con) 
}

close(con)
