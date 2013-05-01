
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
## @madlib-param hetero The heteroskedasticity flag, boolean
## @madlib-param incr_ The count of the test cases, when _incr is 1, create the answer file
## @madlib-param ans.path_ The answer file path

dataset <- as.character(dataset)
hetero <- as.logical(toupper(hetero))

## ------------------------------------------------------------------------

## Other parameters
target <- "y"                  # dependent variable
predictors <- "~ . - 1"        # fitting formula
grouping.cols <- character(0)  # grouping column name VECTOR
not.xcols <- grouping.cols     # exclude these columns

## ------------------------------------------------------------------------

tincrepo <- Sys.getenv("TINCREPOHOME")

suppressMessages(library(lmtest))
suppressMessages(library(car))
source(paste(tincrepo, "/madlib/src/r_utils/utils.R", sep = ""))

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")
data.path = paste(ans.path_, "/data/", sep = "")
system(paste("rm -rf", data.path))
system(paste("mkdir", data.path))
py.path = paste(tincrepo, "/madlib/src/r_utils", sep = "")

result.file <- paste(ans.path_, "/linregr_test2.ans", sep = "")

if (incr_ == 1) system(paste("rm -f", result.file))

## ------------------------------------------------------------------------

con <- file(result.file, "a")

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
    ##
    ## ----------------------------------------------------------------
    ## All the previous parts should be refactored out later, and can be
    ## utilized in other modules that support grouping
    ## The following computation & output parts are just module-specific
    ##
    ## Actual computation part
    fit <- lm(formula(paste(target, predictors)), data = dat.use)
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
