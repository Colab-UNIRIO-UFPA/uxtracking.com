import os
import pandas as pd
userid = 'fb50a10f11b0c153e88e96d06668911f'
datadir=f'./Samples/{userid}'

datamap = {}
folders = list(filter(lambda x: os.path.isdir(os.path.join(datadir, x)), os.listdir(datadir)))
for page in os.listdir(datadir):
    datamap[page] = []
    for date in os.listdir(os.path.join(datadir, page)):
        # Lendo os traços em csv 
        df = pd.read_csv(os.path.join(datadir, page, date, 'trace.csv'))
        datamap[page].append({date:df.type.unique()})

print(datamap)