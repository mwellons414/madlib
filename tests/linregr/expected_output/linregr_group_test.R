
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
## @madlib-param g String of comma-separated values for groups


display_dataset <- as.character(dataset)
dataset <- paste(as.character(dataset), "_oi", sep = "")
hetero <- as.logical(toupper(hetero))
grouping.cols <- gsub(" ", "", strsplit(as.character(g), ",")[[1]])

print(grouping.cols)

## ------------------------------------------------------------------------

## Other parameters
target <- "y"                  # dependent variable
predictors <- " ~ . "          # fitting formula
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

result.file <- paste(ans.path_, "/linregr_test_group.ans", sep = "")

if (incr_ == 1) system(paste("rm -f", result.file))

## ------------------------------------------------------------------------

con <- file(result.file, "a")

name <- dataset
dat <- prepare.dataset.grouping(name, sql.path = sql.path,
                        data.path = data.path,
                        py.path = py.path)

## The independent variable columns
xcols <- setdiff(names(dat), c(target, not.xcols))
predictors <- paste(" ~ ",  paste(xcols, collapse="+"))       # fitting formula
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
coefs <- {}
r2 <- {}
std_err <- {}
t_value <- {}
p_value <- {}
kappa <- {}

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
    kp <- kappa(fit, exact = TRUE)

    ## Conctenate all the answers
    coefs <- c(coefs, fit$coefficients)                      # coef
    r2 <- c(r2 , fit.sum$r.square)                         # r.square
    std_err <- c(std_err, fit.sum$coefficients[(1:l) + l])   # std err
    t_value <- c(t_value, fit.sum$coefficients[(1:l) + 2*l]) # t value
    p_value <- c(p_value, fit.sum$coefficients[(1:l) + 3*l]) # p value
    kappa <- c(kappa, kp)                                    # condition number
}

## File headers
cat(paste(display_dataset, "\n", sep = ""), file = con)
cat(paste(as.character(hetero), "\n", sep = ""), file = con)
# Write to a file
output.vec(coefs, con) 
output.vec(r2, con) 
output.vec(std_err, con) 
output.vec(t_value, con) 
output.vec(p_value, con) 
output.vec(kappa, con) 
cat("\n", file = con)
close(con)
