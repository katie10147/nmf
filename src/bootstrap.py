"""
For each device:

    1. load the data
    2. execute NMF analysis for x factors

Results/Export:
    1. dataframe with time series of factors and all other data
    2. composition
"""
import pandas as pd
from sklearn.decomposition import NMF
import os

os.chdir('/Users/katiepelton/Desktop/Urban-AQ/Data')

# the number of factors
N_COMPONENTS = 3

COLS_TO_INCLUDE = ['co2', 'co', 'no2', 'o3', 'pm1', 'pm25', 'pm10']

# create an empty array to hold all of the results
frame = []

# load the raw data
df = pd.read_feather('hagan-cleaned.feather').set_index("timestamp_iso")

# drop all rows where there are nans
df = df.dropna(subset=COLS_TO_INCLUDE)

for iter in range(100):

    # set up the nmf analysis
    nmf = NMF(n_components=N_COMPONENTS, alpha=.1, max_iter=500)

    # subselect a portion of the dataset randomly
    sub = df.sample(frac=.5)

    # fit the data
    W = nmf.fit_transform(X=sub[COLS_TO_INCLUDE].T)
    H = nmf.components_

    # convert to a dataframe
    R = pd.DataFrame(H.T, index=sub.index)

    # set the column names
    R.columns = ["Factor {}".format(i) for i in range(H.T.shape[1])]

    # calculate the composition
    comp = pd.DataFrame(W.T, index=R.columns, columns=COLS_TO_INCLUDE)

    # calculate the total and residual for each column
    res = []
    for i, col in enumerate(comp.columns):
        by_factor = pd.DataFrame(comp.iloc[:, i].values * H.T).sum()

        # divide by the total amount for a given species
        by_factor /= sub[col].sum()

        res.append(pd.DataFrame(by_factor, columns=[col]).T)
    
    res = pd.concat(res)
    res.columns = R.columns
    res["Residual"] = 1 - res.sum(axis=1)

    res = res.reset_index().melt(id_vars=["index"])

    # add in a few more columns
    res["iter"] = iter
    frame.append(res)

# concat and save the data
frame = pd.concat(frame, sort=False)

# save the data
frame.to_csv('bs.csv')
frame.reset_index().to_feather('bs.feather')