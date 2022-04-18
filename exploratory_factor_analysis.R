# -----------------------------------------------
# EFA
# -----------------------------------------------

library(dplyr)
# -----------------------------------------------
# build dataframe
# -----------------------------------------------
df <- data.frame(data$commits_ma3,
                 data$comments_ma3,
                 data$PR_open_ma3,
                 data$authors_ma3,
                 data$contributor_count.,
                 data$updated_since.,
                 data$forks)

df = rename(df, commits = data.commits_ma3,
            comments = data.comments_ma3,
            PR = data.PR_open_ma3,
            authors = data.authors_ma3,
            contributors = data.contributor_count.,
            updated = data.updated_since.,
            forks = data.forks)

# -----------------------------------------------
# Factor analysis with LAVAAN 
# -----------------------------------------------
library(tidyverse)
library(lavaan)

# single factor model syntax
f1 <- '
efa("efa")*f1 =~ commits + comments + PR + authors + contributors + updated + forks
'

# two-factor model syntax
f2 <- '
efa("efa")*f1 +
efa("efa")*f2 =~ commits + comments + PR + authors + contributors + updated + forks
'

efa_f1 <- 
  cfa(model = f1,
      data = df,
      rotation = "varimax",
      estimator = "WLSMV",
      ordered = TRUE)

summary(efa_f1, fit.measures = TRUE)

efa_f2 <- 
  cfa(model = f2,
      data = df,
      rotation = "geomin",
      estimator = "WLSMV",
      ordered = TRUE)

summary(efa_f2, fit.measures = TRUE)

efa_f2vm <- 
  cfa(model = f2,
      data = df,
      rotation = "varimax",
      estimator = "WLSMV",
      ordered = TRUE)

summary(efa_f2vm, fit.measures = TRUE)

# -----------------------------------------------
# Factor analysis with PSYCH
# -----------------------------------------------
library(psych)
# install.packages(c("GPArotation"))
library(GPArotation)
fa_model = fa(df,1)
fa_model
