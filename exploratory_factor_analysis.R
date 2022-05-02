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
                 data$forks,
                 data$stars)

df = rename(df, commits = data.commits_ma3,
            comments = data.comments_ma3,
            PR = data.PR_open_ma3,
            authors = data.authors_ma3,
            contributors = data.contributor_count.,
            updated = data.updated_since.,
            forks = data.forks,
            stars = data.stars)

df_noUpdated = subset(df, select=-c(updated))
df_noContributors = subset(df, select=-c(contributors))
df_noSF = subset(df, select=-c(stars,forks))

df_eng <- data.frame(data$commits_ma3,
                 data$comments_ma3,
                 data$PR_open_ma3,
                 data$authors_ma3
                 )

df_eng = rename(df_NF, commits = data.commits_ma3,
            comments = data.comments_ma3,
            PR = data.PR_open_ma3,
            authors = data.authors_ma3)

# -----------------------------------------------
# correlation matrix plot
# -----------------------------------------------
library(psych)
plot<-cor.plot(df,numbers=TRUE,main="Indicator Correlation Matrix")
# to output the matrix to the console
print(plot)

# this one looks better
# https://cran.r-project.org/web/packages/corrplot/vignettes/corrplot-intro.html 
library(corrplot)
corrplot(cor(df), method="shade", tl.col="black", addCoef.col = 'black', diag=F,type='lower', order='FPC')

# -----------------------------------------------
# Bartlett's test
# https://personality-project.org/r/html/cortest.bartlett.html
# https://www.statology.org/bartletts-test-of-sphericity/
# -----------------------------------------------
cortest.bartlett(cor(df), 211, diag=TRUE)
cortest.bartlett(cor(fa_model$residual),211, diag=TRUE)

# -----------------------------------------------
# MSO (KMO) Test Measure of Sampling Adequacy (MSA) 
# of factor analytic data matrices
# https://www.personality-project.org/r/html/KMO.html
#-----------------------------------------------

KMO(cor(df))

# output:
# Kaiser-Meyer-Olkin factor adequacy
# Call: KMO(r = cor(df))
# Overall MSA =  0.73
# MSA for each item = 
#   commits     comments           PR      authors contributors      updated        forks 
# 0.88         0.71         0.68         0.88         0.80         0.81         0.52 
  
# -----------------------------------------------
# scree plot shows two factors for this dataset
# -----------------------------------------------
scree(df,factors=TRUE,pc=TRUE,main="Scree plot",hline=NULL,add=FALSE) 
VSS.scree(df, main = "scree plot")
# see the eigenvalues
print(scree(df))

# -----------------------------------------------
# Factor analysis with LAVAAN 
# -----------------------------------------------
library(tidyverse)
library(lavaan)

# Supported rotation methods are: 
# varimax, quartimax, orthomax, cf, oblimin, quartimin,
# geomin, entropy, mccammon, infomax,tandem1, tandem2, oblimax,
# bentler, simplimax, target, pst, crawford-ferguson, cf-quartimax,
# cf-varimax, cf-equamax, cf-parsimax, cf-facparsim

# single factor model syntax
f1 <- '
efa("efa")*f1 =~ commits + comments + PR + authors + contributors + updated + forks
'

# two-factor model syntax
f2 <- '
efa("efa")*f1 +
efa("efa")*f2 =~ commits + comments + PR + authors + contributors + updated + forks
'

# three-factor model syntax
f3 <- '
efa("efa")*f1 +
efa("efa")*f2 +
efa("efa")*f3 =~ commits + comments + PR + authors + contributors + updated + forks
'

efa_f1 <- 
  cfa(model = f1,
      data = df_scale,
      rotation = "none",
      estimator = "MLM",
      ordered=FALSE)

summary(efa_f1, fit.measures = TRUE)

efa_f2 <- 
  cfa(model = f2,
      data = df_scale,
      rotation = "oblimin",
      estimator = "MLM",
      ordered = FALSE)

summary(efa_f2, fit.measures = TRUE, standardized=TRUE)


summary(efa_f2vm, fit.measures = TRUE)

# Scale the whole data.frame
df_scale <- apply(df,  2, scale)

efa_f2qm <- 
  cfa(model = f1,
      data = df_scale,
      rotation = "quartimax"
      )

summary(efa_f2qm, fit.measures = TRUE)

efa_f3 <- 
  cfa(model = f3,
      data = df_scale,
      rotation = "none",
      estimator = "MLM")
summary(efa_f3, fit.measures = TRUE)


# -----------------------------------------------
# Factor analysis with PSYCH
# documentation: https://cran.r-project.org/web/packages/psychTools/vignettes/factor.pdf
# p.18 for factor methods
# -----------------------------------------------
library(psych)
# install.packages(c("GPArotation"))
library(GPArotation)
fa_model = fa(df,2,fm="ml",rotate="varimax")
fa_model = fa(df_noUpdated,2,fm="ml",rotate="quartimax")
fa_model = fa(df_noSF,2,fm="pa",rotate="oblimin")
fa_model = fa(df2,2,fm="pa",rotate="oblimin")
fa_model = fa(df_noContributors,2,fm="ml")
fa_model = fa(df_eng,1,fm="pa",rotate="oblimin")
fa_model = fa(df_eng,1,fm="mr")

print(fa_model,cut=0,digits=3)
fa_model

df2 <- data.frame(data$commits_ma3,
                 data$comments_ma3,
                 data$PR_open_ma3,
                 data$authors_ma3,
                 data$contributor_count.,
                 data$updated_since.,
                 data$forks,
                 data$stars,
                 data$criticality_score.,
                 data$alexa_rank,
                 data$med_resp_time_days,
                 data$avg_longevity_days)

df2 = rename(df2, commits = data.commits_ma3,
            comments = data.comments_ma3,
            PR = data.PR_open_ma3,
            authors = data.authors_ma3,
            contributors = data.contributor_count.,
            updated = data.updated_since.,
            forks = data.forks,
            stars = data.stars,
            crit = data.criticality_score.,
            rank = data.alexa_rank,
            resp = data.med_resp_time_days,
            long = data.avg_longevity_days)




# to report on the structural coefficients (for oblique rotation methods)
# if the factor correlation matrix is close to 0, then
# pattern coefficients (standard loadings) ~= structure coefficients
fa_model$Structure


# factor methods
# fm="pa" -> principal axis
# fm="wls" -> weighted least squares
#
# fm="minres" -> default, factor.minres attempts to minimize the off diagonal residual correlation matrix by adjusting
# the eigen values of the original correlation matrix. This is similar to what is done in factanal,
#  but uses an ordinary least squares instead of a maximum likelihood fit function. The solutions tend
# to be more similar to the MLE solutions than are the factor.pa solutions. min.res is the default
# for the fa function.


# diagrams/plots
fa.diagram(fa_model)
plot(fa_model)

# info
print(fa_model$residual)
corrplot(cor(fa_model$residual), method="shade", tl.col="black", addCoef.col = 'black', diag=T,type='lower')

print(fa_model,cut=0,digits=3)


# -----------------------------------------------
# Factor analysis with EPMR
# -----------------------------------------------
install.packages("devtools")
devtools::install_github("talbano/epmr")
library(epmr)
library(base)
library("ggplot2")
em_fit <- fastudy(df, factors = 2)
print(em_fit, digits = 3)
print(em_fit, digits = 2, cutoff = 0.3)

# recode the updates since (months) column to have the high metric
# representative as positive and the lower as negative
updated_r <- rescore(df$updated)
dstudy(updated_r)

# change df['updated'] to updated_r and redo results
df$updated <- updated_r
dstudy(df$updated)

# -----------------------------------------------
# CFA on df_noUpdated:
# -----------------------------------------------
# df <- data.frame(data$commits_ma3,  F1
#                  data$comments_ma3, F1
#                  data$PR_open_ma3,  F1
#                  data$authors_ma3,  F1
#                  data$contributor_count., F2
#                  data$forks,        F2
#                  data$stars)        F2  
# -----------------------------------------------

# Scale the whole data.frame
df_scale_nu <- apply(df_noUpdated,  2, scale)

# step 1: model specification
cfa1 <- '
      # measurement models
      ENG =~ commits + comments + PR + authors
      POP =~ contributors + forks + stars
     
      # residual covariance
      # authors ~~ contributors
      
      # covariance structure
      # AG ~~ OP+PR
      # OP ~~ PR
      # AG ~~ AG
      # OP ~~ OP
      # PR ~~ PR
'
# STEP 2: model estimate
#
cfa1.fit <- sem(  cfa1,
                  data = df_scale_nu,
                  estimator = "MLM",
                  meanstructure = FALSE)

#step 3: evaluate the model
summary(cfa1.fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# visualize the model
library(semPlot)
semPaths(cfa1.fit,
         rotation=2,
         layout="tree2",
         what="std",
         posCol="black",
         edge.width=0.5,
         style="Lisrel",
         fade=T,
         edge.label.position=0.55)
