#!/usr/bin/env python
import numpy as np
import pandas as pd
import plotnine as pn
import os as os
from mizani.transforms import trans

import sys


def trade_level_plots(dir, match, mismatch, murex, smart, type, facet, xLabelSuffix=None):
    if not os.path.exists(dir):
        sys.exit('Could not find path ' + dir)

    match = dir + '/' + match
    if not os.path.exists(match):
        sys.exit('Could not find path ' + match)

    mismatch = dir + '/' + mismatch
    if not os.path.exists(mismatch):
        sys.exit('Could not find path ' + dir)

    df = pd.concat([pd.read_csv(match, sep=','), pd.read_csv(mismatch, sep=',')], sort=True)

    npvs = (murex, smart)
    df.loc[:, npvs] = df.loc[:, npvs].apply(pd.to_numeric)

    df['absChange'] = abs(df[murex] - df[smart])
    df['relChange'] = abs(df['absChange'] * 100 / df[murex])
    df.loc[(df[murex] == 0) & (df[smart] == 0), "relChange"] = 0
    df.loc[(df[murex] == 0) & (df[smart] != 0), "relChange"] = 100

    if 'CURRENCY' in df:
        df.loc[(df['CURRENCY'] != 'EUR') & (df['CURRENCY'] != 'USD') & (df['CURRENCY'] != 'GBP'), "CURRENCY"] = 'OTHER'
    else:
        df['CURRENCY'] = 'OTHER'

    y_break = [float(pow(10., i)) for i in np.arange(0, np.ceil(np.log10(len(df))), 1)]

    start = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, ]
    x_break = start + [float(pow(10., i)) for i in np.arange(0, np.ceil(np.log10(max(df['relChange'])+1)) + 1, 1)]

    class linearlog_trans(trans):
        domain = (0, np.inf)

        @staticmethod
        def transform(x):
            return pd.Series([(i * 10. if i <= 1 else np.log10(i) + 10) for i in x])

        @staticmethod
        def inverse(x):
            return pd.Series([(i / 10. if i <= 1 else pow(10, i - 10)) for i in x])

    xLabelSuffix = xLabelSuffix if xLabelSuffix else ' Error % Murex vs Smart (VM pricing)'

    base = (pn.ggplot(df, pn.aes('relChange', '..count..'))
            + pn.stat_bin(breaks=x_break, color='white', fill='black')
            + pn.coord_trans(linearlog_trans, 'log1p')
            + pn.scale_y_continuous(breaks=y_break, labels=pretty, minor_breaks=[], name='Frequency')
            + pn.scale_x_continuous(breaks=x_break, labels=pretty, minor_breaks=[],
                                    name=type + xLabelSuffix)
            + pn.theme_classic()
            + pn.theme(axis_text_x=pn.element_text(rotation=90, size=8, hjust=.5), axis_text_y=pn.element_text(size=8),
                       figure_size=(16.5, 11.7)))
    p1 = (base
          + pn.geom_text(pn.aes(y='..count..', label='..count..'), nudge_y=.5, stat="bin", va='bottom',

                         format_string='{:.0f}', breaks=x_break, fontweight=8)
          + pn.geom_text(pn.aes(y='..count.. * 0', label='..count.. * 100/ sum(..count..)'), nudge_y=.5, stat="bin",
                         va='bottom', color='white', format_string='{:.2f}%', breaks=x_break, fontweight=8))
    if (facet):
        p2 = (base
              + pn.facet_grid(['CURRENCY', 'LCH_PRODUCT_TYPE'], scales='free_x', drop=True))
        return [p1, p2]
    else:
        return [p1]



def main(dir):
    p = []

    try:
        p = trade_level_plots(dir, 'NpvMatchRec.csv', 'NpvMismatchRec.csv', 'MX_NPV', 'SMART_NPV', 'NPV', True)
        p += trade_level_plots(dir, 'DeltaMatchRec.csv', 'DeltaMismatchRec.csv', 'MX_DVO1', 'SMART_DVO1', 'DVO1', True)
    except:
        print ('Fail to generate Npv|Delta Recs')

    try:
        p += trade_level_plots(dir, 'AccountRec_Intersect_MarginMismatch.csv', 'AccountRec_Intersect_MarginMatch.csv',
                              'E_TOTAL_IM', 'A_TOTAL_IM', 'TOTAL_IM', False,' Error % Murex(FullReval) vs Smart(Taylor) using murex sensitivities')
        p += trade_level_plots(dir, 'AccountRec_Intersect_MarginMismatch.csv', 'AccountRec_Intersect_MarginMatch.csv',
                               'E_IM', 'A_IM', 'IM', False, ' Error % Murex(FullReval) vs Smart(Taylor) using murex sensitivities')
        p += trade_level_plots(dir, 'AccountRec_Intersect_MarginMismatch.csv', 'AccountRec_Intersect_MarginMatch.csv',
                               'E_LIQ', 'A_LIQ', 'LIQ', False, ' Error % Murex vs Smart using murex sensitivities' )
        p += trade_level_plots(dir, 'AccountRec_Intersect_MarginMismatch.csv', 'AccountRec_Intersect_MarginMatch.csv',
                               'E_BRA', 'A_BRA', 'BRA', False, ' Error % SmartServices(Murex Sensitivities vs SmartFpml(Fpml sensitivities)')
        p += trade_level_plots(dir, 'AccountRec_Intersect_MarginMismatch.csv', 'AccountRec_Intersect_MarginMatch.csv',
                               'E_UNSCALED', 'A_UNSCALED', 'UNSCALED', False,
                               ' Error % SmartServices(Murex Sensitivities vs SmartFpml(Fpml sensitivities)')
    except:
        print('Fail to generate some|all of Account Level Recs')

    try:
        p += trade_level_plots(dir, 'Account_BucketedSensitivity_Match.csv', 'Account_BucketedSensitivity_Mismatch.csv',
                           'M_Z_DELTA','F_Z_DELTA', 'ZERO DELTA', False,
                           ' Error % Murex vs Fpml Zero Delta')
        p += trade_level_plots(dir, 'Account_BucketedSensitivity_Match.csv', 'Account_BucketedSensitivity_Mismatch.csv',
                               'M_Z_GAMMA','F_Z_GAMMA', 'ZERO GAMMA', False,
                               ' Error % Murex vs Fpml Zero Gamma')
    except:
        print('Fail to generate Bucket Sensitivity Recs')

    pn.save_as_pdf_pages(p, filename="plots.pdf", path=dir)


def pretty(b):
    return ["{:,.2f}".format(i).rstrip('0').rstrip('.') for i in b]


if __name__ == "__main__":
    main(sys.argv[1])
