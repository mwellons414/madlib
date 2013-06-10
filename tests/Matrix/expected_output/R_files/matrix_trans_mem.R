## @madlib-param dataset The data set name, string
## @madlib-param method.name_ The answer file path
## @madlib-param ans.path_ The answer file path

dataset <- as.character(dataset)

## ------------------------------------------------------------------------
tincrepo <- Sys.getenv("TINCREPOHOME")

sql.path = paste(tincrepo, "/madlib/datasets/sql/", sep = "")
data.path = paste(ans.path_, "/data/", sep = "")
system(paste("rm -rf", data.path))
system(paste("mkdir", data.path))
py.path = paste(ans.path_, "/R_files", sep = "")
method.prefix = sub(".sql", "", method.name_)

result.file <- paste(ans.path_, "/", method.prefix, ".ans", sep = "")
## ------------------------------------------------------------------------

name <- dataset

system(paste("rm -rf ", data.path, "/", dataset, ".*", sep=""))
system(paste("cp ", sql.path, "/", dataset, ".sql.gz ", data.path, sep=""))
system(paste("gunzip ", data.path, "/", dataset, ".sql.gz", sep=""))
system(paste("python ", py.path, "/sql2csv_mem.py ", data.path, "/", dataset, ".sql ", data.path, "/", dataset, ".csv", sep=""))

m <- read.csv(paste(data.path, "/", dataset, ".csv", sep = ""), FALSE)
m <- as.matrix(m)
m_t <-t(m)
write(t(m_t), result.file, ncolumns = dim(m_t)[2], sep=",")
