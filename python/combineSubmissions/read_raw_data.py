'''
read raw member data, format and store (in database)
'''

import numpy as np
import pandas as pd
import os
import re

if __name__ == "__main__":

    # directory containing date stamped directories with member data
    data_dir = "//swpdv33/F$/Compilations/20180601_Swaptions/data/RAW data"

    # directories are assumed to contain date stamped
    ds = [f for f in os.listdir(data_dir) if f.isdigit()]

    # member names - try to figure out member from name
    mem_names = ["DB", "CNN", "NOI"]

    # column name map
    csv_col_map = {'EXP': 'expiry', 'TAIL':'maturity', 'RELATIVE_STRIKE': 'strike', 'NORM_VOL': 'vol', 'FWD':'fwd'}
    xlsx_col_map = {'Expiry': 'expiry', 'Maturity': 'maturity', 'Strike': 'strike', 'Volatility': 'vol', 'Forward Rate':'fwd'}

    # keep columns
    keep_col = ['expiry', 'maturity', 'strike', 'vol', 'fwd', 'mem', 'ccy', 'date', 'file_name']

    # column names map
    col_map = {'csv': csv_col_map,
               'xlsx': xlsx_col_map}

    # store results in a list
    results = []

    # increment over the date stamped directories
    for d in ds:
        print(d)
        date_dir = data_dir + '/' + d
        # get ccys - directories
        ccys = [x for x in os.listdir(date_dir) if os.path.isdir(date_dir + '/' + x)]
        for c in ccys:
            # get the files - drop and files starting with ~
            ccy_dir = date_dir + '/' + c
            fs = [x for x in os.listdir(ccy_dir) if not bool(re.search('^~', x))]
            for f in fs:
                file_name = ccy_dir + '/' + f
                # csv?
                if bool(re.search('.csv$', f)):
                    df = pd.read_csv(file_name)
                    df.rename(columns=csv_col_map, inplace=True)
                elif bool(re.search('.xlsx$', f)):
                    try:
                        df = pd.read_excel(file_name)
                        df.rename(columns=xlsx_col_map, inplace=True)
                    except:
                        print('issue with: %s - %s - %s'%(d,c,f))
                        continue
                else:
                    print('file not recognised, continuing: %s - %s - %s' % (d, c, f))
                    continue


                # add ccy and file name (get member from file name later)
                guess_name = [m for m in mem_names if bool(re.search(m, f))]
                if len(guess_name) == 1:
                    mname = guess_name[0]
                else:
                    mname = ''
                # df['date'] = d
                df['date'] = np.datetime64(pd.to_datetime(d, format='%Y%m%d'))
                df['ccy'] = c
                df['mem'] = mname
                df['file_name'] = f
                results += [df[keep_col].copy()]

    tmp = pd.concat(results)
    out_file = 'combined_raw_data.csv'
    try:
        # try moving the current file to archive 
        from swapclear.utils import moveToArchive
        moveToArchive(data_dir, out_file)
    except:
        # don't move to archive if have no access to swapclear
        pass
    
    #tmp.to_csv(data_dir + '/' + out_file, index=False)

    #pivot data to be in smart / py tool format

    tt = pd.pivot_table(tmp, index = ['date','ccy', 'expiry', 'maturity', 'strike'], values ='vol', columns = 'mem')
    ttOrg = tt.copy()
    ttv = ttOrg.values
    for i in np.arange(len(ttOrg)):
        x = ttv[i,:]
        #check for nans
        if np.isnan(x).any():
            if np.isnan(x).sum() == 1:
                x[np.isnan(x)] = x[~np.isnan(x)].mean()
            else:
                x[np.isnan(x)] = x[~np.isnan(x)]

    xx = ttOrg.reset_index()
    yy = tt.reset_index()
    xx.rename(columns={'expiry': 'Expiry', 'maturity': 'Maturity', 'strike':'Strike'}, inplace=True)
    yy.rename(columns={'expiry': 'Expiry', 'maturity': 'Maturity', 'strike': 'Strike'}, inplace=True)

    dcy = xx[['date','ccy']].drop_duplicates()

    #only want to produce subset of columns
    drop_cols = ['date','ccy']
    keep_col = [x for x in xx.columns if not x in drop_cols]

    for i in np.arange(len(dcy)):
        tm = dcy.iloc[i]
        #select subset
        d = tm.date
        c = tm.ccy

        y = xx[(xx.date == d) & (xx.ccy == c)]
        z = yy[(yy.date == d) & (yy.ccy == c)]
        datestamp = d.strftime('%Y%m%d')
        out_file = '%s_%s_memcont.csv'%(datestamp, c)
        out_file2 = '%s_%s_memcont_RAW.csv' % (d.strftime('%Y%m%d'), c)

        out_file_full = '%s/%s/%s/%s'%(data_dir, datestamp, c, out_file)
        out_file_full2 = '%s/%s/%s/%s' % (data_dir, datestamp, c, out_file2)

        y[keep_col].to_csv(out_file_full, index=False)
        z[keep_col].to_csv(out_file_full2, index=False)



