# -----------------------------------------------
# SEM
# -----------------------------------------------
# lets get this done!
#
install.packages(c("epmr"))
install.packages("devtools")
install.packages("devtools", type = "win.binary")
library(devtools)
devtools::install_github("talbano/epmr")
library(epmr)
# -----------------------------------------------
# load data
# -----------------------------------------------
# select data (after cleaning)
data <- read.csv("healthData_388.csv")
print(data)

# -----------------------------------------------
# build dataframe
# -----------------------------------------------
library(dplyr)
df <- data.frame(data$stars,
                 data$forks,
                 data$alexa_rank,
                 data$dependents_count.,
                 data$geo_mae,
                 #data$geo_rmse,
                 data$criticality_score.,
                 data$avg_longevity_days,
                 #data$med_resp_time,
                 #data$avg_resp_time,
                 data$updated_since.
                 #data$days_inactive
                 )

# df for lavaan model
dfl <- data.frame(data$stars,
                  data$forks,
                  data$alexa_rank,
                  data$dependents_count.,
                  data$authors,
                  data$commits,
                  data$PR_open,
                  data$comments,
                  data$geo_mae,
                  data$criticality_score.,
                  data$avg_longevity_days,
                  data$updated_since.
)

dfl = rename(dfl, 
             stars = data.stars,
             forks = data.forks,
             rank = data.alexa_rank,
             dependents = data.dependents_count.,
             auth = data.authors,
             commits = data.commits,
             prs = data.PR_open,
             comments = data.comments,
             geo = data.geo_mae,
             crit = data.criticality_score.,
             long = data.avg_longevity_days,
             updated = data.updated_since.
)

# data$updated_since. has zeroes meaning updating within the month
# set them to 0.5 *before* rescoring
dfl["updated"][dfl["updated"] == 0] <- 0.5

# -----------------------------------------------
# rescore data for valence
# -----------------------------------------------
# 
geo_r        <- rescore(dfl$geo)
updated_r    <- rescore(dfl$updated)
rank_r       <- rescore(dfl$rank)
dfl$geo      <- geo_r 
dfl$updated  <- updated_r 
dfl$rank     <- rank_r 

# -----------------------------------------------
mydata <- summarytools::descr(updated_since._r,round.digits = 1)
mydata2 <- summarytools::descr(df$data.updated_since.,round.digits = 1)


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


# -----------------------------------------------
# scree plot shows two factors for this dataset
# -----------------------------------------------
scree(df,factors=TRUE,pc=TRUE,main="Scree plot",hline=NULL,add=FALSE) 
VSS.scree(df, main = "scree plot")
# see the eigenvalues
print(scree(df))


# -----------------------------------------------
# Factor analysis with PSYCH
# documentation: https://cran.r-project.org/web/packages/psychTools/vignettes/factor.pdf
# p.18 for factor methods
# -----------------------------------------------
library(GPArotation)

# subset dataframes
df_noAuthors = subset(df, select=-c(authors))
df_noInactive = subset(df, select=-c(inactive))

# run the model
# varimax for 2 or more; quartimax for single factor
# ML, known to perform well when the factor-variable relationships are strong. 
# PA priciple axis method was also used for comparison purposes as it is ideal for non-normality and small sample sizes
fa1 = fa(df,4,fm="ml",rotate="varimax")
fa1 = fa(df, 2, fm="ml", missing=TRUE, rotate="varimax")
fa1 = fa(df, 2, fm="ml", rotate="varimax")
fa1

# display the results
print(fa1,cut=0.2,digits=3)
fa1
plot(fa1)
ggsave("fa1.png")


# -----------------------------------------------
# on to SEM...
# -----------------------------------------------
# lets get this done!
#
# Model 1: Regression model with manifest variables only
#------------------------------------
library(lavaan)
factors <- c("interest", "robustness", "engagement")
# Model specification (using lavaan syntax)
sem <- '
# latent factors
  interest =~   stars + forks + dependents + rank
  robustness =~ crit + geo + long + updated
  engagement =~ auth + commits + comments + prs 
--------
interest =~ prs
interest =~    commits

# regressions
robustness ~ engagement + interest
engagement ~ interest
'

# model estimate
# least convergence issues from SEM functions

# Scale the whole data.frame
dfl_scaled <- apply(dfl, 2, scale)

fit <- sem(sem, data = dfl_scaled, estimator = "MLM")
summary(fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

fitMeasures(fit, c("cfi","rmsea","srmr"))
install.packages("Rtools")
library(semPlot)
semPaths(fit2.a, whatLabels = "std", edge.label.cex = .5, layout = "tree2", rotation = 2, style = "lisrel", intercepts = FALSE, residuals = TRUE, curve = 1, curvature = 3, nCharNodes = 8, sizeMan = 6, sizeMan2 = 3, optimizeLatRes = TRUE, edge.color = "#000000")
semPaths(fit2.a, what = "est", layout = "tree", title = TRUE, style = "LISREL")

library(dplyr)
modificationindices(fit, sort = TRUE)
modificationindices(fit2) %>%
  as_data_frame() %>%
  arrange(-mi) %>%
  filter(mi > 11) %>%
  select(lhs, op, rhs, mi, epc)

  #pander(caption="Largest MI values for hz.fit")
