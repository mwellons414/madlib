
## ------------------------------------------------------------------------

## strip pattern from the beginning and end of the string
strip <- function(string, pattern)
{
    m <- paste("^[", pattern, "]*|[", pattern, "]*$")
    gsub(m, "", string)
}

## ------------------------------------------------------------------------

## Elastic Net log-likelihood for linear models

log.likelihood <- function(x, y, coef, a0, lambda, alpha, scaling = FALSE)
{
    s <- 0
    for (i in seq(length(y)))
    {
        t <- sum(coef * x[i,]) + a0 - y[i]
        s <- s + 0.5 * t^2
    }
    s <- s / length(y)
    if (!scaling)
    {
        s <- s + 0.5 * lambda * (1 - alpha) * sum(coef * coef) + lambda * alpha * sum(abs(coef))
    }
    else
    {
        xsd <- apply(x, 2, sd) * sqrt(1 - 1./length(y))
        s <- s + 0.5 * lambda * (1- alpha) * sum((coef * xsd)^2) + lambda * alpha * sum(abs(coef * xsd))
    }
    ##
    as.numeric(-s)
}

## ------------------------------------------------------------------------

## Elastic Net log-likelihood for logistic models

log.likelihood2 <- function(x, y, coef, a0, lambda, alpha, scaling = FALSE)
{
    s <- 0
    for (i in seq(length(y)))
    {
        t <- sum(coef * x[i,]) + a0
        if (y[i] == TRUE)
            s <- s + log(1 + exp(-t))
        else
            s <- s + log(1 + exp(t))
    }
    s <- s / length(y)
    if (!scaling)
    {
        s <- s + 0.5 * lambda * (1 - alpha) * sum(coef * coef) + lambda * alpha * sum(abs(coef))
    }
    else
    {
        xsd <- apply(x, 2, sd) * sqrt(1 - 1./length(y))
        s <- s + 0.5 * lambda * (1- alpha) * sum((coef * xsd)^2) + lambda * alpha * sum(abs(coef * xsd))
    }
    as.numeric(-s)
}


## ------------------------------------------------------------------------

output.vec <- function(vec, con)
{
    l <- length(vec)
    for (k in 1:l) {
        if (is.null(vec[k]) || is.infinite(vec[k]) || is.na(vec[k]))
            cat("Null", file = con)
        else
            cat(vec[k], file = con)
        if (k != l)
            cat(", ", file = con)
        else
            cat("\n", file = con)
    }
}

## ------------------------------------------------------------------------

prepare.dataset <- function(dataset, sql.path = "../../dataset/sql/",
                            data.path = "../data/", py.path = ".", py.script = "sql2r.py")
{
    w1 <-  system(paste("ls -ld ", sql.path, sep = ""),
                  ignore.stdout = TRUE, ignore.stderr = TRUE)
    w2 <-  system(paste("ls -ld ", data.path, sep = ""),
                  ignore.stdout = TRUE, ignore.stderr = TRUE)
    if (w1 != 0)  # 0 is the success return code
        stop("sql.gz path does not exist!")
    if (w2 != 0)  
        stop("data path does not exist!")
    
    z <- system(paste("ls ", sql.path, "/", dataset, ".sql.gz", sep = ""),
                ignore.stdout = TRUE, ignore.stderr = TRUE)
    if (z != 0) return (NULL)
    z1 <- system(paste("ls ", data.path, "/", dataset, ".sql", sep = ""),
                 ignore.stdout = TRUE, ignore.stderr = TRUE)
    z2 <- system(paste("ls ", data.path, "/", dataset, ".txt", sep = ""),
                 ignore.stdout = TRUE, ignore.stderr = TRUE)
    if (z1 != 0 || z2 != 0)
    {
    	system(paste("rm -rf ", data.path, "/", dataset, ".*", sep=""))
        system(paste("cp ", sql.path, "/", dataset, ".sql.gz ", data.path, sep=""))
        system(paste("gunzip ", data.path, "/", dataset, ".sql.gz", sep=""))
        system(paste("python ", py.path, "/", py.script, "  ", data.path, "/", dataset, ".sql ", data.path, "/", dataset, ".txt", sep=""))
    }
    ##
    dat <- read.csv(paste(data.path, "/", dataset, ".txt", sep = ""))
    return (dat)
}
## ------------------------------------------------------------------------

prepare_cox.dataset <- function(dataset, sql.path = "../../dataset/sql/",
                            data.path = "../data/", py.path = ".")
{
    w1 <-  system(paste("ls -ld ", sql.path, sep = ""),
                  ignore.stdout = TRUE, ignore.stderr = TRUE)
    w2 <-  system(paste("ls -ld ", data.path, sep = ""),
                  ignore.stdout = TRUE, ignore.stderr = TRUE)
    if (w1 != 0)  # 0 is the success return code
        stop("sql.gz path does not exist!")
    if (w2 != 0)  
        stop("data path does not exist!")
    ##
    z <- system(paste("ls ", sql.path, "/", dataset, ".sql.gz", sep = ""),
                ignore.stdout = TRUE, ignore.stderr = TRUE)
    if (z != 0) return (NULL)
    z1 <- system(paste("ls ", data.path, "/", dataset, ".sql", sep = ""),
                 ignore.stdout = TRUE, ignore.stderr = TRUE)
    z2 <- system(paste("ls ", data.path, "/", dataset, ".txt", sep = ""),
                 ignore.stdout = TRUE, ignore.stderr = TRUE)
    if (z1 != 0 || z2 != 0)
    {
        system(paste("rm -rf ", data.path, "/", dataset, ".*", sep=""))
        system(paste("cp ", sql.path, "/", dataset, ".sql.gz ", data.path, sep=""))
        system(paste("gunzip ", data.path, "/", dataset, ".sql.gz", sep=""))
        system(paste("python ", py.path, "/sql2r_cox.py ", data.path, "/", dataset, ".sql ", data.path, "/", dataset, ".txt", sep=""))
    }
    ##
    dat <- read.csv(paste(data.path, "/", dataset, ".txt", sep = ""))
    return (dat)
}

