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
mydata393 <- summarytools::descr(df,round.digits = 3,stats = c("mean", "sd", "min", "med", "max"),transpose=T)
print(mydata393)
# full data / all columns
mydata390 <- summarytools::descr(df_no_out,round.digits = 1)
# subset for paper
mydata390 <- summarytools::descr(df_no_out,round.digits = 1,stats = c("mean", "sd", "min", "med", "max"),transpose=T)
print(mydata390)


dataStFk <- df[,c(7:8)]
dataStFk_noBTC <- df_no_out[,c(7:8)]
dataPRcomments <- df[,c(2:3)]
dataPRcomments_noOUT <- df_no_out[,c(2:3)]
# corr matrix with histogram, scatter, etc.
pairs.panels(dataPRcomments_noOUT,
             smooth = TRUE,      # If TRUE, draws loess smooths
             scale = F,      # If TRUE, scales the correlation text font
             density = TRUE,     # If TRUE, adds density plots and histograms
             ellipses = TRUE,    # If TRUE, draws ellipses
             method = "pearson", # Correlation method (also "spearman" or "kendall")
             pch = 21,           # pch symbol
             bg=c("yellow"),
             lm = T,         # If TRUE, plots linear fit rather than the LOESS (smoothed) fit
             cor = TRUE,         # If TRUE, reports correlations
             jiggle = FALSE,     # If TRUE, data points are jittered
             factor = 2,         # Jittering factor
             hist.col = 4,       # Histograms color
             stars = TRUE,       # If TRUE, adds significance level with stars
             ci = TRUE)          # If TRUE, adds confidence intervals


# -----------------------------------------------
# Cullen and Frey
# -----------------------------------------------
# What dist does my data follow?
# https://stats.stackexchange.com/questions/58220/what-distribution-does-my-data-follow
#
library(fitdistrplus)
descdist(df$PR, discrete=FALSE)
f1 <- fitdist(scaled_commits_ma3,"beta",method="mme")



# -----------------------------------------------
# correlation matrix plot
# -----------------------------------------------
# this one looks better
# https://cran.r-project.org/web/packages/corrplot/vignettes/corrplot-intro.html 
library(psych)
library(corrplot)
# Pearson is the default correlation method in cor(df)
corrplot(cor(df),
         method="shade", 
         tl.col="black", 
         addCoef.col = 'black', 
         diag=F, 
         type='lower')
last_plot()
library(ggplot2)
ggsave("corrMatrix1.png")
ggsave(
  filename = "corrMatrix1.png",
  plot = last_plot(),
  #path = C:\Users\jnijsse\OneDrive - AUT University\PhD\Engagement Paper\hicss_latex_format_specifications\images,
  scale = 1,
  dpi = 600,
  limitsize = TRUE,
  bg = NULL,
)
#, order='FPC'
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
df_noSt_Fk_out = subset(df_no_out, select=-c(stars,forks))
df_noSt_Fk_AuT_out = subset(df_no_out,select=-c(stars, forks, authorsT))

df_devEng = subset(df_noSt_Fk, select=-c(authorsT,inactive))

fa_model1 = fa(df,2,fm="ml",rotate="varimax")
fa_model2 = fa(df,2,fm="ml",rotate="quartimax")
fa_model2b =fa(df_noSt_Fk,2,fm="ml",rotate="quartimax")
fa_model2c =fa(df,1,fm="ml",rotate="quartimax")

fa_model3 = fa(df,2,fm="mr",rotate="varimax")
fa_model4 = fa(df,2,fm="mr",rotate="quartimax")
fa_model5 = fa(df,2,fm="pa",rotate="oblimin")
fa_model6 = fa(df,2,fm="pa",rotate="oblimin")
fa_model2
fa_model6

fa_model3 = fa(df_noSt_Fk_out,2,fm="ml",rotate="quartimax") ## BEST FIT STARS AND FORKS REMOVED
fa_model4 = fa(df,2,fm="ml",rotate="varimax")


# compare with and without top 3 influential observations
# (393 of 6) no stars/forks
df_noSt_Fk 
# (390 of 6) no stars/forks
df_noSt_Fk_out
# (390 of 5) no stars/forks/authorsT
df_noSt_Fk_AuT_out

fa_393=fa(df_noSt_Fk,2,fm="ml",rotate="quartimax")
fa_390=fa(df_noSt_Fk_AuT_out,2,fm="ml",rotate="quartimax")
fa_393
fa_390

fa_model1$TLI
fa_model2$TLI
fa_model3$TLI
fa_model4$TLI

fa_model1$RMSEA
fa_model2$RMSEA
fa_model3$STATISTIC
fa_model4$RMSEA


print(fa_model,cut=0,digits=3)
fa_model
plot(fa_model)
ggsave("model.png")
# test for the number of factors in your data using parallel analysis
fa.parallel(df,fa="fa")
PAout<-fa.parallel(df,fa="fa")

# VSS looks inconclusive
vss(df_noSt_Fk)
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
fa.diagram(fa_model, digits=2)
plot(fa_model)

# info
print(fa_model2b$residual)
corrplot(cor(fa_model$residual), method="shade", tl.col="black", addCoef.col = 'black', diag=T,type='lower')

print(fa_model,cut=0,digits=3)


# -----------------------------------------------
# .	Find mahalanobis distance
# -----------------------------------------------
outlier(df, plot=T, bad=3, na.rm=F, cex=0.9)
out<-outlier(df)
out.d2 <-data.frame(df,out)
pairs.panels(out.d2,bg=c("yellow","blue")[(out > 250)+1],pch=21)
out

# -----------------------------------------------
# Remove outliers via D^2
# -----------------------------------------------
head(df)
# 1::BTC, 17::ETH, 210::SOL
df_no_out <- df[-c(1,17,210),]
df_no_out
df_noSt_Fk_out = subset(df_no_out, select=-c(stars, forks))

# full df (8 variables) excluding 3 influential observations
# (390 of 8)
df_no_out

# (393 of 6)
df_noSt_Fk 

# subset df (6 variables) excluding stars and forks
# (390 of 6)
df_noSt_Fk_out

# -----------------------------------------------
# split the dataset for cross validation
# -----------------------------------------------
require(caTools)
set.seed(42) 
sample = sample.split(df_noSt_Fk_out, SplitRatio = 0.5)
train = subset(df_noSt_Fk_out, sample == TRUE)
test  = subset(df_noSt_Fk_out, sample == FALSE)

# -----------------------------------------------
# FA on train for cross validation
# -----------------------------------------------
fa_model_train = fa(train,2,fm="ml",rotate="quartimax")
fa_model_test = fa(test,2,fm="ml",rotate="quartimax")
# -----------------------------------------------
# compare to FA on test for cross validation
# -----------------------------------------------
fa.diagram(fa_model_train, digits=2)
fa.diagram(fa_model_test, digits=2)
fa_model_train
fa_model_test

#
#
#
##
#
##
#
##
#
##
#
##
#
##
#
##
#
##
#
##
#

# -----------------------------------------------
# Factor analysis with EPMR
# -----------------------------------------------
install.packages("devtools")
devtools::install_github("talbano/epmr")
library(epmr)
library(base)
library("ggplot2")
em_fit <- fastudy(df_devEng, factors = 1)
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



