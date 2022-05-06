# -----------------------------------------------
# EFA
# -----------------------------------------------
# sessionInfo()
# 
# R version 4.0.2 (2020-06-22)
# Platform: x86_64-w64-mingw32/x64 (64-bit)
# Running under: Windows 10 x64 (build 19041)
# 
# other attached packages:
# [1] semPlot_1.1.2        lavaan_0.6-8         forcats_0.5.1        stringr_1.4.0        purrr_0.3.4         
# [6] readr_2.1.2          tidyr_1.2.0          tibble_3.1.6         ggplot2_3.3.5        tidyverse_1.3.1     
#[11] GPArotation_2022.4-1 psych_2.2.3          dplyr_1.0.8     

# package installation
install.packages(c("summarytools"))

# -----------------------------------------------
# load data
# -----------------------------------------------
# select data (after cleaning)
f <- file.choose()
data <- read.csv(f)

# -----------------------------------------------
# build dataframe
# -----------------------------------------------
library(dplyr)
df <- data.frame(data$commits_ma3,
                 data$comments_ma3,
                 data$PR_open_ma3,
                 data$authors_ma3,
                 data$auth_tot,
                 data$days_inactive,
                 data$stars_tot,
                 data$forks_tot)
                 

df = rename(df, 
            commits  = data.commits_ma3,
            comments = data.comments_ma3,
            PR       = data.PR_open_ma3,
            authors  = data.authors_ma3,
            authorsT = data.auth_tot,
            forks    = data.forks_tot,
            stars    = data.stars_tot,
            inactive = data.days_inactive)



# recode the Inactive Since (days) column to have the high metric
# representative as positive and the lower as negative
library(epmr)
updated_inactive <- rescore(df$inactive)
# change df['updated'] to updated_r and redo results
df$inactive <- updated_inactive

# df_noUpdated = subset(df, select=-c(updated))
# df_noContributors = subset(df, select=-c(contributors))
# df_noSF = subset(df, select=-c(stars,forks))
# 
# df_eng <- data.frame(data$commits_ma3,
#                      data$comments_ma3,
#                      data$PR_open_ma3,
#                      data$authors_ma3
# )
# 
# df_eng = rename(df_NF, commits = data.commits_ma3,
#                 comments = data.comments_ma3,
#                 PR = data.PR_open_ma3,
#                 authors = data.authors_ma3)

# -----------------------------------------------
# Descriptive stats
# -----------------------------------------------
# library(knitr)
# dat_des <- data.frame(describe(data))
# dat.df <- t(dat_des)
# kable(dat.df)
# 
# library(psych)
# describe(data, mat=T)
# 
# library(Hmisc)
# Hmisc::describe(data)

# see link for summaryTools options
# https://mran.microsoft.com/snapshot/2018-06-19/web/packages/summarytools/vignettes/Introduction.html 
library(summarytools)
mydata <- summarytools::descr(df,round.digits = 1)
print(mydata)


# -----------------------------------------------
# correlation matrix plot
# -----------------------------------------------
# this one looks better
# https://cran.r-project.org/web/packages/corrplot/vignettes/corrplot-intro.html 
library(psych)
library(corrplot)
corrplot(cor(df), method="shade", tl.col="black", addCoef.col = 'black', diag=F,type='lower', order='FPC')

# -----------------------------------------------
# Bartlett's test
# https://personality-project.org/r/html/cortest.bartlett.html
# https://www.statology.org/bartletts-test-of-sphericity/
# -----------------------------------------------
cortest.bartlett(cor(df), 393, diag=TRUE)
cortest.bartlett(cor(fa_model$residual), 393, diag=TRUE)

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
library(GPArotation)
df_noAuthors = subset(df, select=-c(authors))
df_noInactive = subset(df, select=-c(inactive))
df_noAuth_noIn = subset(df_noInactive, select=-c(authors))
df_noAuthorsT = subset(df, select=-c(authorsT))
df_noSt_Fk = subset(df, select=-c(stars, forks))
df_noSt_Fk_AuT = subset(df, select=-c(stars, forks, authorsT))

fa_model = fa(df,2,fm="pa",rotate="oblimin")
fa_model = fa(df_noAuth_noIn,2,fm="pa",rotate="oblimin")
fa_model = fa(df_noInactive,2,fm="pa",rotate="oblimin")
fa_model = fa(df_noAuthorsT,2,fm="pa",rotate="oblimin")
fa_model = fa(df_noSt_Fk,2,fm="pa",rotate="oblimin")

fa_model1 = fa(df,2,fm="ml",rotate="varimax")
fa_model2 = fa(df_noAuth_noIn,2,fm="ml",rotate="varimax")
fa_model3 = fa(df_noInactive,2,fm="ml",rotate="varimax")
fa_model4 = fa(df_noAuthorsT,2,fm="ml",rotate="varimax")
fa_model5 = fa(df_noAuthors,2,fm="ml",rotate="varimax")
fa_model6 = fa(df_noSt_Fk_AuT,2,fm="ml",rotate="varimax")


fa_model1 = fa(df,2,fm="pa",rotate="oblimin")
fa_model2 = fa(df,2,fm="ml",rotate="quartimax")
fa_model3 = fa(df,2,fm="ml",rotate="varimax") # best fit
fa_model4 = fa(df,2,fm="mr")

fa_model1$TLI
fa_model2$TLI
fa_model3$TLI
fa_model4$STATISTIC
fa_model5$STATISTIC
fa_model6$STATISTIC


print(fa_model,cut=0,digits=3)
fa_model1
plot(fa_model)

# test for the number of factors in your data using parallel analysis
fa.parallel(df)
vss(df)

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
