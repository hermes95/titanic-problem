# coding: utf-8

## -- MODULES -- ##
import numpy as np
import pandas as pd
import sklearn.ensemble as ske
from patsy import dmatrices
from sklearn.cross_validation import train_test_split

## -- HELPER FUNCTIONS -- ##
def name_extract(word):
    return word.split(',')[1].split('.')[0].strip()


# Return Type --> {Mr,Master,Mrs,Miss}
def group_salutation(old_salutation):
    if old_salutation == 'Mr' or old_salutation == 'Master':
        return (old_salutation)
    elif old_salutation == 'Mrs' or old_salutation == 'Mme':
        return ('Mrs')
    elif old_salutation == 'Miss' or old_salutation == 'Mlle':
        return ('Miss')
    else:
        return ('Others')


# Return Type --> numSiblings, ifMarried #
def split_sibsp(row):
    sibsp = row['SibSp']
    age = row['Age']
    if (sibsp == 0): return (0, 0)
    if (age < 25): return (sibsp, 0)
    return (sibsp - 1, 1)


# Return Type --> numParents, numChildren
def split_parch(row):
    age = row['Age']
    parch = row['Parch']
    married = row['Married']
    if (married == 0 and parch > 2): return (2, parch - 2)
    if (married == 0 and parch < 2): return (parch, 0)

    # Its more likely that he will come with his children than parents

    if (parch > 2): return (2, parch - 2)
    if (parch <= 2): return (parch, 0)

    return (0, 0)


# Return Type --> {Children, Adults, Elderly}
def group_age(age):
    if (age < 18):
        return ('Children')
    elif (age < 50):
        return ('Adults')
    else:
        return ('Elderly')


### --- Groups passengers by their salutation (Mr., Mrs., Miss, Master) --- ###
def map_salutation(df):
    df2 = pd.DataFrame({'Salutation': df['Name'].apply(name_extract)})
    df = pd.merge(df, df2, left_index=True, right_index=True)  # merges on index

    df3 = pd.DataFrame({'New_Salutation': df['Salutation'].apply(group_salutation)})
    df = pd.merge(df, df3, left_index=True, right_index=True)
    return df


### --- Groups passengers by their Age (Children, Adults, Elderly) --- ###
def map_ages(df):
    df4 = pd.DataFrame({'Age_Class': df['Age'].apply(group_age)})
    df = pd.merge(df, df4, left_index=True, right_index=True)
    return df


### --- Split SibSp into Siblings & Spouse --- ###
def map_sibsp(df):
    df['Siblings'], df['Married'] = zip(*df.apply(split_sibsp, axis=1))
    return df


### --- Split Parch into Parents & Children --- ###
def map_parch(df):
    df['Parents'], df['Children'] = zip(*df.apply(split_parch, axis=1))
    return df

## -- PREPROSESSING ANALYSIS -- ##
# Removing rows and columns that are None
df = pd.read_csv("train.csv")
df = df.drop(['Ticket', 'Cabin'], axis=1)
# Remove NaN values
df = df.dropna()

df = map_salutation(df)
df = map_ages(df)
df = map_sibsp(df)
df = map_parch(df)


## -- MODEL -- ##
formula = 'Survived ~ C(Pclass) + C(Sex) + Fare + C(Embarked) + C(New_Salutation) + C(Age_Class) + Married + Siblings'
# create a results dictionary to hold our regression results for easy analysis later
results = {}
score = 0
for i in range(100):
    train_data, test_data = train_test_split(df, test_size=0.25)

    # Create the random forest model and fit the model to our training data
    y, x = dmatrices(formula, data=train_data, return_type='dataframe')
    # RandomForestClassifier expects a 1 demensional NumPy array, so we convert
    y = np.asarray(y).ravel()
    # instantiate and fit our model
    results_rf = ske.RandomForestClassifier(n_estimators=100).fit(x, y)

    # Score the results
    y, x = dmatrices(formula, data=test_data, return_type='dataframe')
    score = score + results_rf.score(x, y)

print "Mean accuracy of Random Forest Predictions on the data was: {0}".format(score / 100)


## -- PROBLEMS -- ##
# A single parent will go with his/her children, and this can be determined using family names and ages
