
## -----------------------------------------------------------------------
## Generate R results for validation
## -----------------------------------------------------------------------

library(lmtest)
library(car)

source("../../src/r_utils/utils.R")

## linear regression R result
hsd.append.results <- function(datasets, hsd = TRUE, 
                               sql.path = "~/workspace/testsuite/dataset/sql/",
                               data.path = "data/", py.path = "../../src/r_utils")
{
    con <- file("linregr_test.ans", "a")
    for (i in seq_along(datasets))
    {
        name <- datasets[i]
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
            if (hsd) {
                ## bp <- bptest(fit)
                ## cf <- coeftest(fit, vcov = hccm(fit, type = "hc0"))
                bp <- list(statistic = 0, p.value = 0.9)
                cf <- rep(0, 4*l)
            } 
            kp <- kappa(fit, exact = TRUE)
            ##
            cat(paste(name, "\n", sep = ""), file = con)
            cat(paste(as.character(hsd), "\n", sep = ""), file = con)
            output.vec(fit$coefficients, con) # coef
            cat(paste(fit.sum$r.square, "\n", sep = ""), file = con) # coef
            output.vec(fit.sum$coefficients[(1:l) + l], con) # std err
            output.vec(fit.sum$coefficients[(1:l) + 2*l], con) # t value
            output.vec(fit.sum$coefficients[(1:l) + 3*l], con) # p value
            cat(paste(kp, "\n", sep = ""), file = con) # condition number
            if (hsd) {
                cat(paste(bp$statistic, "\n", sep = ""), file = con)
                cat(paste(bp$p.value, "\n", sep = ""), file = con)
                ## output.vec(cf[(1:l) + l], "double precision[]", ",\n", con)
                ## output.vec(cf[(1:l) + 2*l], "double precision[]", ",\n",  con)
                ## output.vec(cf[(1:l) + 3*l], "double precision[]", ");\n\n",  con)
            }
            cat("\n", file = con)
        }
    }
    close(con)
}

## ------------------------------------------------------------------------

datasets <- c("lin_auto_mpg_wi", "lin_auto_mpg_oi")

hsd.append.results(datasets, hsd = TRUE);
hsd.append.results(datasets, hsd = FALSE);

