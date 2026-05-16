import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.api as sm


file="C:/Users/c04-labuser1020554/Documents/Phase2/day 1_day2/foundational_capabilities/dataset/2_fraud.csv"
data=pd.read_csv(file)
print(data.dtypes)

#catgorial column
fc=list(data.select_dtypes(include=['object','category']).columns.values)
print(fc)
#remove not catgorial coulmn
cols_remove=['transaction_id', 'customer_id', 'txn_timestamp']
for c in cols_remove:
    fc.remove(c)

print(fc)

#convert Fc into numerical representation
#one hot encoding

#make dummy variables for all category columns
new_data = data.copy()
for c in fc:
    dummy = pd.get_dummies(new_data[c], drop_first=True, prefix=c)
    new_data = new_data.join(dummy)

new_data.customer_segment.unique()
print(new_data.dtypes)

#remove old columns from data set
new_data.drop(columns=fc, inplace=True)
print(new_data)

#booleans columsn anything is convert into int
bc = new_data.select_dtypes(include=['bool']).columns
if len(bc) > 0:
    new_data[bc] = new_data[bc].astype(int)

Y = "is_fraud"

trainx, testx, trainy, testy = train_test_split(new_data.drop(Y, axis=1), new_data[Y], test_size=0.1)

print(trainx.shape)
print(trainy.shape)

print(testx.shape)
print(testy.shape)

trainx.head(1)
trainy.head(1)

testx.head(1)
testy.head(1)

#Build the Classification Model
#Logistic Regression

# model = sm.Logit(trainy, trainx).fit()

trainx.dtypes
trainy.dtypes

trainx.drop(columns=cols_remove, inplace=True)
testx.drop(columns=cols_remove, inplace=True)

model = sm.Logit(trainy, trainx).fit()

#predict the model in test data
p1 = model.predict(testx)

print(p1[:10])

#---------------------

'''
ANOVA finds potentially important features
FDR decides which ones are trustworthy after correcting for multiple comparisons.
'''

from sklearn.feature_selection import f_classif, SelectFdr

f_statistic, pvalue = f_classif(trainx, trainy)
df_fstats = pd.DataFrame({"feature": trainx.columns, "fstat": f_statistic, "pvalue": pvalue})

print(df_fstats)

selector = SelectFdr(score_func=f_classif, alpha=0.05)
selector.fit_transform(trainx, trainy)
df_fdr = pd.DataFrame({"feature": trainx.columns, "f_score": selector.scores_, "p_value": selector.pvalues_,
                       "selected": selector.get_support()})
df_fdr = df_fdr.sort_values("selected", ascending=False)

print(df_fdr)

data.is_fraud.value_counts()

