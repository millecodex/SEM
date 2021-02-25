# required packages
#install.packages(c("lavaan","semPlot","MPsychoR","corrplot"))
library(lavaan)
library(semPlot)
library(MPsychoR)
library(corrplot)

#select data
data("Bergh")
View(Bergh)
attach(Bergh)

#sample size
nrow(Bergh)

#create the mean scores as new variables and insert into Bergh dataset
Bergh$Open <- (O1+O2+O3)/3
Bergh$Agree <- (A1+A2+A3)/3
Bergh$Prejudice <- (EP+SP+DP+HP)/4

# Model 1: Regression model with manifest variables only
#------------------------------------
# Model specification (using lavaan syntax)
model1 <- '
    # structural relations
    Prejudice ~ b1*Open + b2*Agree
    
    # covariances and variances
    Open ~~ Agree
    Open ~~ Open
    Agree ~~ Agree
'
# model estimate
# least convergence issues from SEM functions
model1.fit <- sem(model1,
                  data = Bergh,
                  estimator = "ML",
                  meanstructure = FALSE)

# set rsquare = TRUE to answer how much variation is explained by the two other variables
# standardized = TRUE
# does this model really fit? fit.measures = TRUE
summary(model1.fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# residuals to check the discrepancy between the two covariance matrices
# residuals of zero show the model is perfectly identified
resid(model1.fit, type = "raw")

# model-implied covariance matrix
fitted(model1.fit)

# all parameters together
parameterestimates(model1.fit)

# test hypothesis that b1=b2
# a bit lost about this
lavTestWald(model1.fit, constraints = "b1==b2")

#------------------------------------------
# model 2
# introduce a MEDIATION variable between the others
model2 <- '
    # structural relations
    Prejudice ~ b1*Open + b2*Agree
    Open ~ b3*Agree
    
    # covariances and variances 
    Agree ~~ Agree
    
    # new parameter that can be estimated by lavan
    # indirect parameter to represent the indirect relationship
    # of two variables through another one
    ind := b1*b3
'
#step 2, model estimation
model2.fit <- sem(model2,data=Bergh,meanstructure=FALSE,estimator="ML")

#step 3: evaluate the model
summary(model2.fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# visualize the model
semPaths(model2.fit,
         rotation=2,
         layout="tree2",
         what="std",
         posCol="black",
         edge.width=0.5,
         style="Lisrel",
         fade=T,
         edge.label.position=0.55)

#-------------------------------------------
# Model 3: LATENT variables (CFA)
# step 1: model specification
model3 <- '
      # measurement models
      AG =~ A1+A2+A3
      OP =~ O1+O2+O3
      PR =~ EP+SP+HP+DP
      
      # covariance structure
      AG ~~ OP+PR
      OP ~~ PR
      AG ~~ AG
      OP ~~ OP
      PR ~~ PR
'
# STEP 2: model estimate
#
model3.fit <- sem(model3,
                  data = Bergh,
                  estimator = "ML",
                  meanstructure = FALSE)

#step 3: evaluate the model
summary(model3.fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# visualize the model
semPaths(model3.fit,
         rotation=2,
         layout="tree2",
         what="std",
         posCol="black",
         edge.width=0.5,
         style="Lisrel",
         fade=T,
         edge.label.position=0.55)

#-------------------------------------------
# Model 3b: LATENT variables (CFA)
# introduce covariance between A1 and A3 OUTSIDE
# the relationship indicated by the latent factor
# (this could be stars<-->forks together independent of health)
# the Test Statistic (chi-squared) for Model 3 was a bit high (difference between the matrices); this one is better
# step 1: model specification
model3b <- '
      # measurement models
      AG =~ A1+A2+A3
      OP =~ O1+O2+O3
      PR =~ EP+SP+HP+DP
      
      # covariance structure
      AG ~~ OP+PR
      OP ~~ PR
      AG ~~ AG
      OP ~~ OP
      PR ~~ PR
      
      # residual covariance
      A1 ~~ A3
'
# STEP 2: model estimate
#
model3b.fit <- sem(model3b,
                  data = Bergh,
                  estimator = "ML",
                  meanstructure = FALSE)

#step 3: evaluate the model
summary(model3b.fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# visualize the model
semPaths(model3b.fit,
         rotation=2,
         layout="tree2",
         what="std",
         posCol="black",
         edge.width=0.5,
         style="Lisrel",
         fade=T,
         edge.label.position=0.55)

# model comparison: 3 vs 3b: how much better is it?
anova(model3.fit,model3b.fit)
# -> much much better

#-------------------------------------------
# Model 4: STRUCTURAL EQUATION MODEL (yay)
# # step 1: model specification
model4 <- '
      # structural relationships
      PR ~ b1*AG + b2*OP
      
      # measurement models
      AG =~ A1+A2+A3
      OP =~ O1+O2+O3
      PR =~ EP+SP+HP+DP
      
      # residual covariance
      A1 ~~ A3
'
# STEP 2: model estimate
#
model4.fit <- sem(model4,
                   data = Bergh,
                   estimator = "ML",
                   meanstructure = FALSE)

#step 3: evaluate the model
summary(model4.fit,
        rsquare = TRUE,
        standardized = TRUE,
        fit.measures = TRUE)

# visualize the model
semPaths(model4.fit,
         rotation=2,
         layout="tree2",
         what="std",
         posCol="black",
         edge.width=0.5,
         style="Lisrel",
         fade=T,
         edge.label.position=0.55)

# hypothesis testing
lavTestWald(model4.fit, constraints = "b1==b2")

