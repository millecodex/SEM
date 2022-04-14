# required packages
# install.packages(c("lavaan","semPlot","MPsychoR","corrplot","fitdistrplus"))
library(lavaan)
library(semPlot)
library(MPsychoR)
library(corrplot)
# to scale certain variables in the dataframe
library(dplyr)

# library(fitur)
# library(actuar)
# install.packages(c("actuar"))
# install.packages(c("Rtools"))

# distribution stuffs
# ZIP: Zero-inflated poisson regression is used to model count data that has an excess of zero counts
# "did you catch fish?" many will answer no; 0.
#
# check normality of data using two tests:
# parametric tests expect normally distributed data; non-parametric tests do not assume normality
# stack exchange says these methods are bollocks
# 1. Shapiro-Wilk Test
#    > smaller data sets
# 2. KS Kolmogorov-Smirnov test
#    > larger, more than 100 observations
#    > for a continuous distribution and does not allow for ties/duplicates
# Alexa Rankings -> cuberoot data is closest to normal: Shapiro-Wilk normality test W = 0.97031, p-value = 0.03899
# criticality -> W = 0.98399, p-value = 0.7382, so IS normal


# select data (after cleaning)
f <- file.choose()
data <- read.csv(f)
head(data)
View(data)

# The database is attached to the R search path. This means that the database 
# is searched by R when evaluating a variable, so objects in the database can 
# be accessed by simply giving their names.
attach(data)
names(data)

# simple plot of 2 variables
plot(data$criticality_score., log(data$commits_ma3))
plot(data$criticality_score., data$contributor_count.)

# simple histogram
hist(created_since.)
hist(comment_frequency.)
hist(criticality_score.)
hist(commit_frequency.)
hist(log(commit_frequency.))
hist(contributor_count.)

# take a look at skew 
library(moments)
# normal data is 0 skew; >2 is trouble (non-normal)
# negative skew has most data on the right
# positive skew has most data on the left
print(skewness(data$criticality_score.))   #-0.12
print(skewness(data$commit_frequency.))    #3.184
print(skewness(data$comment_frequency.))   #2.32
print(skewness(data$contributor_count.))   #2.80
print(skewness(data$closed_issues_count.)) #8.48

# take a look at kurtosis
# <3 is platykurtic, and has a flatness about the peak
# ~3 is mesokurtic, or about normal
# >3 is leptokurtic, and has a sharp peak
print(kurtosis(data$criticality_score.))   #2.098
print(kurtosis(data$commit_frequency.))    #15.2
print(kurtosis(data$comment_frequency.))   #11.9
print(kurtosis(data$contributor_count.))   #10.7
print(kurtosis(data$closed_issues_count.)) #95.2

# scale data for [0,1], e.g. a beta distribution needs this scaling
library(scales)
scaled_commits_ma3 <- rescale(data$commits_ma3)
scaled_comments <- rescale(data$comments_ma3)

library(fitdistrplus)
f1 <- fitdist(data$alexa_rank,"beta",method="mme")
f1 <- fitdist(data$alexa_rank, "norm")
print(f1)
plot(f1)
summary(f1)

data$alexa_rank[64] <- 5000000
data$alexa_rank[64]
data$alexa_rank[123] <- 5000000

# graph of distribution neighborhood
# Cullen and Frey
descdist(data$commits_ma3, discrete=FALSE, boot = 1000)
descdist(scaled_commits_ma3, discrete=FALSE, boot = 1000)
descdist(scaled_comments, discrete=FALSE, boot = 1000)
descdist(data$comments_ma3, discrete=FALSE, boot = 1000)
descdist(scaled_authors, discrete=F, boot = 1000)
descdist(data$alexa_rank, discrete=F, boot = 1000)

# investigate later
# library(fitur)
# library(actuar)
# fitur::fit_dist_addin()

# correlation plots
# see https://r-coder.com/correlation-plot-r/
library(PerformanceAnalytics)
scaledData <- cbind(scaled_authors, scaled_comments, scaled_commits_ma3, scaled_PR)
# method can be pearson, spearman, or kendall
chart.Correlation(scaledData, histogram = TRUE, method = "pearson")

# install.packages("psych")
library(psych)
invRank <- 1/data[,c(7)]
logInvRank <- log(1/data[,c(7)])
dataEngagement <- data[,c(10:13)]
dataInterest   <- data[,c(8:9)]
dataInterest <- cbind(dataInterest, invRank, logInvRank, logRank)
dataInterest <- cbind(dataInterest, invRank)
dataRobustness <- data[,c(6,15:16)]

# corr matrix with histogram, scatter, etc.
pairs.panels(dataRobustness,
             smooth = TRUE,      # If TRUE, draws loess smooths
             scale = FALSE,      # If TRUE, scales the correlation text font
             density = TRUE,     # If TRUE, adds density plots and histograms
             ellipses = TRUE,    # If TRUE, draws ellipses
             method = "pearson", # Correlation method (also "spearman" or "kendall")
             pch = 21,           # pch symbol
             bg=c("yellow"),
             lm = FALSE,         # If TRUE, plots linear fit rather than the LOESS (smoothed) fit
             cor = TRUE,         # If TRUE, reports correlations
             jiggle = FALSE,     # If TRUE, data points are jittered
             factor = 2,         # Jittering factor
             hist.col = 4,       # Histograms color
             stars = TRUE,       # If TRUE, adds significance level with stars
             ci = TRUE)          # If TRUE, adds confidence intervals


# corr matrix COLOR coded
corPlot(data[,c(5:16)], scale=F,numbers=TRUE, upper=FALSE, diag=T, xlas=2,main="All variables correlation matrix")

# factor analysis using the psyche package
# see https://m-clark.github.io/sem/latent-variables.html

fac = fa(dataInterest, nfactors=1, rotate='none')
fac


# # lm is linear models (regression)
# stars.regression <- lm(invAlexa ~ logStars, data=data)
# summary(stars.regression)
# abline(stars.regression, col="blue")
# 
# # tests for normality
# shapiro.test(data$logPR)
# ks.test(data$logRank, "pnorm")
# 
# # scale a column, use center=FALSE to keep positive
# data$alexaScaled <- scale(data[23], center = FALSE)
# alexaScaled
# # convert to inverse (for rank with lower=better)
# data$invAlexa <- 1/(data$alexa_rank)
# # convert to Log (best for analysis)
# data$logStars <- log(data$stars)
# # convert to SquareRoot
# data$sqAlexa <- sqrt(data$Alexa_rank)
# # convert to CubeRoot
# data$cubeAlexa <- (data$Alexa_rank)^(1/3)
# 
# # plot QQ (Quantiles)
# qqnorm(data$logPR, pch = 1, frame = FALSE)
# qqline(data$logPR, col = "steelblue", lwd = 2)
# 
# #create histogram  
# hist(data$logPR, col='coral2', main='-')
# shapiro.test(data$avg_longevity_days)
# 
# ## Scale the whole data.frame
# pilot_data <- apply(pilot_data,  2, scale)

# create single dataframe for lavaan
github <- cbind.data.frame(dataInterest, dataEngagement, dataRobustness)

# Scale the whole data.frame
github_scaled <- apply(github,  2, scale)

# model syntax
# Regression: Y ~ X
# Covariance: Y ~~ X
# Latent variable: eta =~ x1+x2+x3

# Model 1: Regression model with manifest variables only
#------------------------------------
# Model specification (using lavaan syntax)
model1 <- '
    # structural relations
    engagement =~ authors_ma3 + commits_ma3 + comments_ma3 + PR_open_ma3 
    interest =~ stars + forks + invRank
    robustness =~ criticality_score. + med_resp_time_days + avg_longevity_days
'
# model estimate
# least convergence issues from SEM functions
fit <- cfa(model1, data = github_scaled, estimator = "MLM")
# Ill conditioning
# Parameter estimation can be hampered when the variances of variables in the model differ substantially (orders of magnitude)
# We can rescale variables in this case by multiplying by a constant. This has no effect on the fit or interpretation of the model - we just have to recall what the new units represent.
# SOURCE: https://psu-psychology.github.io/r-bootcamp-2018/talks/lavaan_tutorial.html

varTable(fit)
lavInspect(fit, "cov.lv")
# set rsquare = TRUE to answer how much variation is explained by the two other variables
# standardized = TRUE
# does this model really fit? fit.measures = TRUE
summary(fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# residuals to check the discrepancy between the two covariance matrices
# residuals of zero show the model is perfectly identified
resDat <- resid(fit, type = "raw")
corPlot(resDat, scale=F, upper=FALSE, diag=T, main="Residuals Data")
resDat

# model-implied covariance matrix
fitted(fit)

# all parameters together
parameterestimates(model1.fit)

# check distributions: Note that because CFAs (and all SEM models) are based on the covariances among variances, they are susceptible to the effects of violations to the assumption of normality (especially skew and outliers), which can strongly affect covariances.
#install.packages(c("MVN"))
library(MVN)
mini <- data[,22:30]
view(mini)
# see MVN at https://cran.r-project.org/web/packages/MVN/vignettes/MVN.pdf
result <- mvn(data = mini, mvnTest = "royston", univariatePlot = "qqplot")
result <- mvn(data = mini, mvnTest = "royston", univariateTest = "SW", desc = TRUE)
result$univariateNormality
result
min2 <- data[,30:31]
result <- mvn(data = min2, mvnTest = "hz", multivariateOutlierMethod = "quan")
