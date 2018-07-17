'''
read raw member data, format and store (in database)
'''

import numpy as np
import pandas as pd
import os
import re

if __name__ == "__main__":

    data_dir = "D:/home/vishal/temp/swaptions/rawMemberData"

    #directories are assumed to contain date stamped
    ds = [f for f in os.listdir(data_dir) if f.isdigit()]

    #member names - try to figure out member from name
    mem_names = ["DB", "CNN", "NOI"]

    #column name map
    csv_col_map = {'EXP':'expiry','TAIL':'maturity', 'RELATIVE_STRIKE': 'strike', 'NORM_VOL': 'vol', 'FWD':'fwd'}
    xlsx_col_map = {'Expiry':'expiry','Maturity':'maturity', 'Strike': 'strike', 'Volatility': 'vol', 'Forward Rate':'fwd'}

    #keep columns
    keep_col = ['expiry', 'maturity', 'strike', 'vol', 'fwd', 'mem', 'ccy', 'date', 'file_name']

    #column names map
    col_map = {'csv': csv_col_map,
               'xlsx': xlsx_col_map}

    #store results in a list
    results = []
    #increment over the date stamped directories
    for d in ds:
        date_dir = data_dir + '/' + d
        #get ccys - directories
        ccys = [x for x in os.listdir(date_dir) if os.path.isdir(date_dir + '/' + x)]
        for c in ccys:
            dateCurr = []
            #get the files - drop and files starting with ~
            ccy_dir = date_dir + '/' + c
            fs = [x for x in os.listdir(ccy_dir) if not bool(re.search('^~', x))]
            for f in fs:
                dateCurrMem= []
                file_name = ccy_dir + '/' + f
                #csv?
                if bool(re.search('.csv$', f)):
                    df = pd.read_csv(file_name)
                    df.rename(columns=csv_col_map, inplace=True)
                elif bool(re.search('.xslx$',f)):
                    df = pd.read_excel(file_name)
                    df.rename(columns=csv_col_map, inplace=True)

                #add ccy and file name (get member from file name later)
                guess_name = [m for m in mem_names if bool(re.search(m,f))]
                if len(guess_name) == 1:
                    mname = guess_name[0]
                else:
                    mname = ''
                #df['date'] = d
                df['date'] = np.datetime64(pd.to_datetime(d, format='%Y%m%d'))
                df['ccy'] = c
                df['mem'] = mname
                df['file_name'] = f
                dateCurrMem = [df[keep_col].copy()]
                results += dateCurrMem
                dateCurr += dateCurrMem
    tmp = pd.concat(results)
    tmp.to_csv(data_dir + '/' + 'combined_raw_data.csv', index=False)

    print("Finished")


