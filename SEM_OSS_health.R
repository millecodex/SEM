# -----------------------------------------------
# SEM
# -----------------------------------------------
# lets get this done!
#
install.packages(c("epmr"))
install.packages("autoSEM")
install.packages("devtools", type = "win.binary")
devtools::install_github("talbano/epmr")
#
SEM_packages <- c("devtools", "epmr", "dplyr", "psych", "corrplot", "semPlot", "semTools", "lavaan", "GPArotation")   
lapply(SEM_packages, require, character.only = TRUE)
#
# -----------------------------------------------
# load data
# -----------------------------------------------
# select data (after cleaning)
data <- read.csv("healthData_388.csv")
print(data)

# -----------------------------------------------
# build dataframe
# -----------------------------------------------
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
                  #data$alexa_rank,
                  data$CMC_rank,
                  data$dependents_count.,
                  data$authors,
                  data$commits,
                  data$PR_open,
                  data$comments,
                  data$geo_mae,
                  data$criticality_score.
                  #data$avg_longevity_days,
                  #data$updated_since.
)

dfl = rename(dfl, 
             stars = data.stars,
             forks = data.forks,
             cmc = data.CMC_rank,
             #alexa = data.alexa_rank,
             dependents = data.dependents_count.,
             auth = data.authors,
             commits = data.commits,
             prs = data.PR_open,
             comments = data.comments,
             geo = data.geo_mae,
             crit = data.criticality_score.
             #long = data.avg_longevity_days,
             #updated = data.updated_since.
)

# data$updated_since. has zeroes meaning updating within the month
# set them to 0.5 *before* rescoring
dfl["updated"][dfl["updated"] == 0] <- 0.1

# -----------------------------------------------
# rescore data for valence
# -----------------------------------------------
# 
geo_r        <- rescore(dfl$geo)
#updated_r    <- rescore(dfl$updated)
#rank_r       <- rescore(dfl$rank)
cmc_r        <- rescore(dfl$cmc)
dfl$geo      <- geo_r 
#dfl$updated  <- updated_r 
#dfl$rank     <- rank_r 
dfl$cmc      <- cmc_r

# -----------------------------------------------
mydata <- summarytools::descr(updated_since._r,round.digits = 1)
mydata2 <- summarytools::descr(df$data.updated_since.,round.digits = 1)


# -----------------------------------------------
# correlation matrix plot
# -----------------------------------------------
# this one looks better
# https://cran.r-project.org/web/packages/corrplot/vignettes/corrplot-intro.html 
# Pearson is the default correlation method in cor(df)
corrplot(cor(dfl),
         method="shade", 
         tl.col="black", 
         addCoef.col = 'black', 
         diag=F, 
         type='lower')

corrplot(cor(dfl, use = "complete.obs"), method = "circle")
cor(dfl, use = "complete.obs")
corr.test(dfl, adjust="none")
nrow(dfl)
# [1] 388
nrow(na.omit(dfl))
# [1] 385
colSums(is.na(dfl))
# only rank had 3 missing values
# stars      forks      rank dependents auth    commits    prs   comments 
# 0          0          3    0          0       0          0     0

# -----------------------------------------------
# scree plot shows two factors for this dataset
# -----------------------------------------------
scree(dfl,factors=TRUE,pc=TRUE,main="Scree plot",hline=NULL,add=FALSE) 
VSS.scree(df, main = "scree plot")
# see the eigenvalues
print(scree(df))
fa.parallel(dfl)

# -----------------------------------------------
# Factor analysis with PSYCH
# documentation: https://cran.r-project.org/web/packages/psychTools/vignettes/factor.pdf
# p.18 for factor methods
# -----------------------------------------------

# subset dataframes
df_noAuthors = subset(df, select=-c(authors))
df_noInactive = subset(df, select=-c(inactive))

# run the model
# varimax for 2 or more; quartimax for single factor
# ML, known to perform well when the factor-variable relationships are strong. 
# PA priciple axis method was also used for comparison purposes as it is ideal for non-normality and small sample sizes
fa1 = fa(dfl,3, fm="ml", rotate="varimax")
fa1 = fa(df, 3, fm="ml", missing=TRUE, rotate="varimax")
fa1 = fa(df, 2, fm="ml", rotate="varimax")
fa1$loadings
fa1$score.cor
fa1$e.values
fa1
# remove rank
dfl_noRank <- select(dfl,-rank)
# >0.9 suggest multi collinearity
alpha(dfl_noRank)$total$std.alpha
# also remove longevity
dfl_noRankLong <- select(dfl_noRank,-long)
alpha(dfl_noRankLong)$total$std.alpha
alpha(dfl)$total$std.alpha
?reliability

fa1 = fa(dfl_noRankLong,3,fm="ml",rotate="varimax")
fa1$loadings
fa1$score.cor
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
factors <- c("interest", "robustness", "engagement")
# Model specification (using lavaan syntax)
m1 <- '
# latent factors
  interest =~ stars + dependents + forks
  robustness =~ cmc + geo + crit
  engagement =~ auth + prs + comments + commits
'

# scaling
dfl_scaled <- apply(dfl, 2, scale)
describe(dfl_scaled)
# MLR estimator uses robust standard errors to mitigate non-normality
# ML is the default and assumes normality
fit <- cfa(m1, data = dfl_scaled, estimator = "MLR")

summary(fit,
        standardized = TRUE,
        fit.measures = TRUE)

fitMeasures(fit, c("tli", "cfi", "rmsea", "srmr"))

# residuals to check the discrepancy between the two covariance matrices
# residuals of zero show the model is perfectly identified
resid(fit,type = "cor")
corPlot(resDat, scale=F, upper=FALSE, diag=T, main="Residuals Data")
resDat
resDat <- lavResiduals(fit, add.class = TRUE, type = "cor")

reliability(fit)

semPaths(object = fit,
         layout = "tree",
         rotation = 1,
         whatLabels = "std",
         edge.label.cex = 0.75,
         #what = "std",
         edge.color = "black",
         residuals = T)

anova(fit2, fit3)
?fitMeasures
# dfl_scaled is an atomic vector; turn into a dataframe
dfl_scaled_df <- data.frame(dfl_scaled)
describe(dfl_scaled)
# calculate variance
var(dfl_scaled_df$long)


semPaths(fit, whatLabels = "std", edge.label.cex = .5, layout = "tree2", 
         rotation = 2, style = "lisrel", intercepts = FALSE, residuals = T, 
         curve = 1, curvature = 3, nCharNodes = 8, sizeMan = 6, sizeMan2 = 3, 
         optimizeLatRes = TRUE, edge.color = "#000000")
semPaths(fit2.a, what = "est", layout = "tree", title = TRUE, style = "LISREL")

modificationindices(fit, sort = TRUE)

#------------------------------------
# autoSEM
#------------------------------------
devtools::install_github("RJacobucci/autoSEM")
library(autoSEM)

f1.vars <- c("stars","forks","cmc","dependents","auth","commits","prs","comments","geo","crit")
out = autoSEM(method="GA", data=dfl_all_df, nfac=3,
              varList=list(f1.vars), CV=F, std.lv=TRUE,
              criterion="BIC",minInd=2,niter=15)


f1.vars <- c("x1","x2","x3","x4","x5","x6","x7","x8","x9")
out = autoSEM(method="GA",data=myData,nfac=3,
              varList=list(f1.vars),CV=FALSE,
              criterion="RMSEA",minInd=3,niter=3)

facs <- 1:4
out = multFac(facList=facs,parallel="no",method="GA",
              data=myData,orth=FALSE,CV=FALSE,std.lv=TRUE,
              varList=list(f1.vars),criterion="RMSEA",niter="default")

summary(out)
out$solution
out$bestSol
summary.autoSEM
