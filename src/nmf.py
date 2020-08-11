"""
For each device:

    1. load the data
    2. execute NMF analysis for x factors

Results/Export:
    1. dataframe with time series of factors and all other data
    2. composition
"""
import feather
import pandas as pd
from sklearn.decomposition import NMF
import os

os.chdir('/Users/katiepelton/Desktop/Urban-AQ/Data')

# the number of factors
N_COMPONENTS = 3

COLS_TO_INCLUDE = ['co2', 'co', 'no2', 'o3', 'pm1', 'pm25', 'pm10']

# for k, (sn, filepath) in enumerate(zip(snakemake.config['serial_numbers'], snakemake.input)):
df = feather.read_dataframe('hagan-cleaned.feather')

# set the index
df.set_index("timestamp_iso", inplace=True)

# drop all rows where there are nan values in our columns
df = df.dropna(subset=COLS_TO_INCLUDE)

# set up the NMF
nmf = NMF(n_components=N_COMPONENTS, alpha=0.1, max_iter=500)

# fit the data
W = nmf.fit_transform(X=df[COLS_TO_INCLUDE].T)
H = nmf.components_

# convert the results to a dataframe
results = pd.DataFrame(H.T, index=df.index)

# set the column names
results.columns = ["Factor {}".format(i+1) for i in range(H.T.shape[1])]

# calculate the composition
comp = pd.DataFrame(W.T, index=results.columns, columns=COLS_TO_INCLUDE)

# calcualte the total and residual for each column
res = []
for i, col in enumerate(comp.columns):
    by_factor = pd.DataFrame(comp.iloc[:, i].values * H.T).sum()

    # divide by the total ammount for a given species/column
    by_factor /= df[col].sum()

    res.append(pd.DataFrame(by_factor, columns=[col]).T)

res = pd.concat(res)

res.columns = results.columns
res['Residual'] = 1 - res.sum(axis=1)

# merge with the original timeseries
results = pd.merge(df, results, left_index=True, right_index=True, how='outer')

# export the timeseries data
feather.write_dataframe(results.reset_index(), 'timeseries-results.feather')
results.to_csv('timeseries-results.csv')

# export the composition results
feather.write_dataframe(res.reset_index(), 'copmosition-results.feather')
res.to_csv('composition-results.csv')
