"""
"""
import pandas as pd
import numpy as np
import joblib
import feather
import json

import os

log = dict()


os.chdir('/Users/katiepelton/Desktop/urban-aq/nmf/data')

# Import the ACSM results
acsm = pd.read_csv('1d-clean.csv')


# Convert the timestamp to datetimes and then adjust to Kolkata
acsm['timestamp_iso'] = acsm['timestamp_local'].map(pd.to_datetime)

# reverse the order of rows
acsm = acsm.iloc[::-1]

# set the index as the datetime
acsm.set_index("timestamp_iso", inplace=True)
# print(acsm[:10])

# set to kolkata
acsm.index = acsm.index.tz_localize("Asia/Kolkata")

# get rid of extraneous columns
del acsm['timestamp_local']

# convert the column names to lower-case and get rid of the 'CE'
# acsm.columns = [col.lower().split("_")[0] for col in acsm.columns]

log['ACSM'] = {
    'timestamps': {
        'raw': {
            't0': acsm.index[0].isoformat(),
            'tf': acsm.index[-1].isoformat()
        }
    },
    'shape': {
        'raw': acsm.shape
    }
}

# keep only the desired data between t0-tf
acsm = acsm['2020-04-05':'2020-04-15']

# fill in nans with 0
acsm = acsm.fillna(0.)


log['ACSM']['timestamps']['cleaned'] = {
    't0': acsm.index[0].isoformat(),
    'tf': acsm.index[-1].isoformat()
}

log['ACSM']['shape']['cleaned'] = acsm.shape

# load and munge the bc data and add to the acsm data
# bc = pd.read_csv('snakemake.input[1]')

# # convert the time to a datetime
# bc["timestamp_iso"] = bc["BC_local_time"].apply(lambda dt: pd.to_datetime(dt).tz_localize("Asia/Kolkata"))

# # get rid of columns
# del bc["BC_local_time"]

# # change column names
# bc.columns = [col.lower() for col in bc.columns]

# # set the index
# bc.set_index("timestamp_iso", inplace=True)

# # QC.1: Eliminate points below 0 or >= 250.0
# bc = bc.query("bc > 0.0 and bc <= 250.0")

# log['Aethalometer'] = {
#     'timestamps': {
#         'raw': {
#             't0': bc.index[0].isoformat(),
#             'tf': bc.index[-1].isoformat()
#         }
#     },
#     'shape': {
#         'raw': bc.shape
#     }
# }

# # only keep data during the time of interest
# bc = bc[snakemake.config["t0"]: snakemake.config["tf"]]

# # keep only the bc column
# bc = bc[['bc']].copy()

# log['Aethalometer']['timestamps']['cleaned'] = {
#     't0': bc.index[0].isoformat(),
#     'tf': bc.index[-1].isoformat()
# }

# log['Aethalometer']['shape']['cleaned'] = bc.shape


# # merge the two datasets together
# df = pd.merge(acsm, bc, left_index=True, right_index=True, how='outer')

# df = df.sort_index()

# # import the pmf results
# pmf = pd.read_excel(snakemake.input[2], sheet_name="Org Inorg", usecols="A:E")

# # set the column names
# pmf.columns = ['timestamp', 'HOA/BBOA', 'SVOOA', 'LVOOA', 'AC']

# # convert the timestamp to a datetime object
# pmf['timestamp'] = pmf['timestamp'].map(pd.to_datetime)

# # set the timestamp as the index
# pmf.set_index("timestamp", inplace=True)

# # convert to the right timezone
# pmf.index = pmf.index.tz_localize("Asia/Kolkata")

# # resample to 1min data
# pmf = pmf.resample('5min').mean().dropna()

# log['PMF'] = {
#     'timestamps': {
#         'raw': {
#             't0': pmf.index[0].isoformat(),
#             'tf': pmf.index[-1].isoformat()
#         }
#     },
#     'shape': {
#         'raw': pmf.shape
#     }
# }

# # merge with the rest of the data
# pmf = pmf[df.index[0]: df.index[-1]]

# log['PMF']['timestamps']['cleaned'] = {
#     't0': pmf.index[0].isoformat(),
#     'tf': pmf.index[-1].isoformat()
# }

# log['PMF']['shape']['cleaned'] = pmf.shape

# # resample and drop Nans before we merge with PMF data
# df = df.resample('1min').mean().dropna()

# # merge the files together
# df = pd.merge(df, pmf, left_index=True, right_index=True, how='outer')

# # drop all rows where either org or bc is not present
# df = df.dropna(subset=['org', 'bc'])

# # build hte log dictionary to write out
# log['dataset'] = {
#     't0': df.index[0].isoformat(),
#     'tf': df.index[-1].isoformat(),
#     'shape': df.shape
# }

# export the data
acsm.to_csv('1d-munged.csv')

# export to feather
feather.write_dataframe(acsm.reset_index(),'1d-munged.feather')

# # dump the log
# with open(snakemake.output["log"], "w") as f:
#     json.dump(log, f, sort_keys=True, indent=4)