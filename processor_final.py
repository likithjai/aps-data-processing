#!/usr/bin/python3

from pathlib import Path
import pandas as pd
from glob import glob
from datetime import datetime as dt

def dt_formatter(dt_str): #function to format the 'Date' column in meta_df ie dataframe containing the metadata file
    return dt.strptime(dt_str, '%a %b %d %H:%M:%S %Y')

def clean_df(in_df): #cleaning the meta_df. strips column names of leading and trailing whitespaces. deletes any columns where all the values are null, NaN, etc.
    in_df.columns=in_df.columns.str.strip()
    for c in in_df.columns:
        if in_df[c].isnull().all():
            del in_df[c]
    in_df['Date']=in_df['Date'].apply(dt_formatter)
    return in_df

def wax_fnum(row):
    return round(int(row['saxs fnum'])/10)

p=Path('./sections_dir_final')
p.mkdir(parents=True, exist_ok=True)

def file_ops(sample_name,dest_dir=p):
    target=dest_dir/sample_name
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)

pd.set_option('display.max_columns',None)
legend_df=pd.read_excel('SAXSframesvstest_final.xlsx') #contains SAXS frame start, end numbers and SampleNames
buffer_frames=100 #number of frames added to the beginning and end of each section to act as a buffer for context i.e., each section, instead of consisting of SAXS Frame Start to SAXS Frame End, will consist of (SAXS Frame Start - buffer) to (SAXS Frame End + buffer)
readme_str='buffer_frames=100 #number of frames added to the beginning and end of each section to act as a buffer for context i.e., each section, instead of consisting of SAXS Frame Start to SAXS Frame End, will consist of (SAXS Frame Start - buffer) to (SAXS Frame End + buffer)'

meta_df=pd.read_csv('aclarke_jul21_exp_tracking.csv',low_memory=False)
meta_df=clean_df(meta_df)
meta_df['wax fnum']=meta_df.apply(wax_fnum,axis=1)

for idx, row in legend_df.iterrows():
    fnum_lims=[int(i) for i in [row['SAXS Frame Start'],row['SAXS Frame End']]]
    fnum_lims=[el+((-1)**(idex+1)*buffer_frames) for idex,el in enumerate(fnum_lims)]#subtracting buffer_frames from frame start and adding it to frame end
    sample=row['SampleName'].strip()
    fname=sample.replace('/','_')
    print(sample)
    curr_meta=meta_df[['Date', 'MTS load (mm)', 'Furnace T1 (C)',
                       'saxs fnum', 'wax fnum', 'MTS crosshead (mm)']][(meta_df['saxs fnum']>=fnum_lims[0]) & (meta_df['saxs fnum']<=fnum_lims[1])]
    curr_meta.rename({'MTS load (mm)':'Force (N)'}, axis=1, inplace=True)
    file_ops(fname)
    curr_meta.to_csv(p/fname/(fname+'_metadata.csv'),sep=',',index=False)
    with open(p/fname/'readme.txt','w') as f:
        f.writelines(readme_str)

