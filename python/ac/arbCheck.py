import pandas as pd
import numpy as np
import os
import sys
import math


def _npdf(x):
    '''
    normal pdf function
    '''
    res = np.exp(-0.5 * x * x) / np.sqrt(2 * np.pi)
    return res


def _ncdf(x):
    '''normal cdf'''
    # return 0.5 * math.erfc(-x * (1 / math.sqrt(2)))
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def option_norm(f, k, r, t, ts, v, w, annuity):
    '''option pricer - normal underlying'''
    d1 = (f - k) / (v * np.sqrt(t))
    out = np.exp(-r * ts) * annuity * (w * (f - k) * _ncdf(w * d1) + v * np.sqrt(t) * _npdf(d1))
    return out


class ArbChequer(object):

    def __init__(self, notional=1e6, bidAskSpread=2):
        self.notional = notional
        self.bidAskSpread = bidAskSpread / 10000

    def set_input_folder(self, folderPath=os.getcwd(), fileDic={}):

        finalStatus = False
        try:
            self.inputFolder = folderPath
            if not os.path.isdir(folderPath): print('Folder path does not exist')
            text_files = [f for f in os.listdir(folderPath) if f.endswith('.csv')]
            subStr = 'fwdParRates' if not 'fwd' in fileDic.keys() else fileDic['fwd']
            fwdParRatesFile = [s for s in text_files if subStr in s]
            subStr = 'annuityFactors' if not 'ann' in fileDic.keys() else fileDic['ann']
            annuityFactorsFile = [s for s in text_files if subStr in s]
            subStr = 'VolCube' if not 'vol' in fileDic.keys() else fileDic['vol']
            volCubeFile = [s for s in text_files if subStr in s]

            if len(fwdParRatesFile) > 0 and len(annuityFactorsFile) > 0 and len(volCubeFile) > 0:
                self.fwdParRatesFile = fwdParRatesFile[0]
                self.annuityFactorsFile = annuityFactorsFile[0]
                self.volCubeFile = volCubeFile[1]
                finalStatus = True
            else:
                raise NameError('File not found')

        except NameError:
            print('Could not find a file, check folder or name passed to function')
        except:
            print('error with Folder path or-and file names')

        return finalStatus

    def load_files(self):

        finalStatus = False
        try:
            self.rawCleansedVolData = pd.read_csv(self.inputFolder + self.volCubeFile,dtype=
                                                  {'Vol': 'float64'})
            self.expVector = np.sort(self.rawCleansedVolData['Expiry'].unique())
            self.matVector = np.sort(self.rawCleansedVolData['Maturity'].unique())

            print('There are ' + str(len(self.matVector)) + ' unique maturities and ' + str(
                len(self.expVector)) + ' unique expiries')

            if not all(x in self.rawCleansedVolData.columns for x in ['Strike', 'Expiry', 'Maturity', 'Vol']):
                raise Exception('Missing column')

            rawFwdData = pd.read_csv(self.inputFolder + self.fwdParRatesFile, names=self.matVector, index_col=False)
            if not rawFwdData.shape == (len(self.expVector), len(self.matVector)): raise Exception('Fwd Wrong Size')
            rawFwdData['index1'] = self.expVector
            rawAnnuityData = pd.read_csv(self.inputFolder + self.annuityFactorsFile, names=self.matVector,
                                         index_col=False)
            if not rawAnnuityData.shape == (len(self.expVector), len(self.matVector)): raise Exception('Ann Wrong Size')
            rawAnnuityData['index1'] = self.expVector

            annArray = pd.melt(rawAnnuityData, id_vars=['index1'])
            annArray.columns = ['Expiry', 'Maturity', 'Annuity']
            annArray[['Maturity']]=annArray[['Maturity']].astype('int64')
            fwdArray = pd.melt(rawFwdData, id_vars=['index1'])
            fwdArray.columns = ['Expiry', 'Maturity', 'Rate']
            fwdArray[['Maturity']] = fwdArray[['Maturity']].astype('int64')

            self.rawCleansedVolData = pd.merge(self.rawCleansedVolData, annArray, how='left',
                                               left_on=['Expiry', 'Maturity'],
                                               right_on=['Expiry', 'Maturity'])
            self.rawCleansedVolData = pd.merge(self.rawCleansedVolData, fwdArray, how='left',
                                               left_on=['Expiry', 'Maturity'],
                                               right_on=['Expiry', 'Maturity'])

            self.rawCleansedVolData['Call'] = self.rawCleansedVolData.apply( \
                lambda row: option_norm(0, row['Strike'] / 10000.0, 0, row['Expiry'] / 365.0,
                                        row['Maturity'] / 365.0, row['Vol'] / 10000.0, 1,
                                        row['Annuity']) * self.notional, axis=1)

            finalStatus = True

        except Exception as inst:
            x = inst.args
            if x == 'Missing column':
                print('The Volatility csv file is missing one these columns: Strike, Expiry, Maturity, Vol')
            elif x == 'Fwd Wrong Size':
                print('Forward file does not have the expected Maturity/Expiry size implied from the vol file')
            elif x == 'Ann Wrong Size':
                print('Annuity file does not have the expected Maturity/Expiry size implied from the vol file')
            else:
                print('Unexpected error with the csv files: i.e. wrong format, missing columns, etc')
        except:
            print('Unexpected error with the csv files: i.e. wrong format, missing columns, etc')

        return finalStatus

    def runArbChecks(self):

        resultColumn = ['Expiry', 'Maturity', 'Strat', 'Strike1', 'Strike2', 'Strike3', 'ArbLevel']
        arbFailutreDF = pd.DataFrame(columns=resultColumn)
        for m in self.matVector:
            specExpVector = np.sort(
                (self.rawCleansedVolData[(self.rawCleansedVolData['Maturity'] == m)])['Expiry'].unique())
            for e in specExpVector:
                redCleansedVolData = self.rawCleansedVolData[
                    (self.rawCleansedVolData['Expiry'] == e) & (self.rawCleansedVolData['Maturity'] == m)]
                redCleansedVolData = (redCleansedVolData.sort_values(by=['Strike'])).reset_index()
                redCleansedVolData = redCleansedVolData.drop_duplicates(['Strike'])

                ## Condition 1  - Spread Trades
                ##      Cn+1 - Cn < 0 or F'(x) < 0 or monotonically decreasing
                ###################

                sprTrade = np.diff(redCleansedVolData['Call'])

                # central spreads aroud the ATM point
                locATM = (redCleansedVolData.loc[lambda df: df['Strike'] == 0]).index[0]

                if (locATM / redCleansedVolData.shape[0] <= 0.5):
                    locLeft = np.arange(locATM)
                    locRight = np.arange(2 * locATM, locATM, -1)
                else:
                    locLeft = np.arange(2 * locATM + 1 - redCleansedVolData.shape[0], locATM)
                    locRight = np.arange(redCleansedVolData.shape[0] - 1, locATM, -1)

                sprTradeCent = redCleansedVolData['Call'].iloc[locRight].values - \
                               redCleansedVolData['Call'].iloc[locLeft].values

                ## Condition 2 - Butterfly
                ##     C(T,K+∆K) - 2C(K) + C(T,K-∆K) > 0 where ∆K < K
                ##   boils down to  f(x)'' > 0 or function being convex
                ###################

                diffStrike = np.diff(redCleansedVolData['Strike'])
                diff2Strike = diffStrike[0:(diffStrike.shape[0] - 1)] + diffStrike[1:diffStrike.shape[0]]
                callSwaptVec = redCleansedVolData['Call'].values
                secDeriv = callSwaptVec[0:(callSwaptVec.shape[0] - 2)] * diffStrike[
                                                                         1:diffStrike.shape[0]] / diff2Strike - \
                           callSwaptVec[1:(callSwaptVec.shape[0] - 1)] + \
                           callSwaptVec[2:callSwaptVec.shape[0]] * diffStrike[0:(diffStrike.shape[0] - 1)] / diff2Strike

                # central spreads aroud the ATM point
                centButt = redCleansedVolData['Call'].iloc[locLeft].values - \
                           2 * redCleansedVolData['Call'].iloc[locATM] + \
                           redCleansedVolData['Call'].iloc[locRight].values

                #  Record which strategies - points failed
                #################################
                locFail = np.where(sprTrade > self.bidAskSpread * self.notional * 2)
                if (locFail[0].shape[0] > 0):
                    tempArbResult = pd.DataFrame({'Strike1': redCleansedVolData['Strike'].iloc[locFail].tolist(),
                                                  'Strike2': redCleansedVolData['Strike'].iloc[locFail[0] + 1].tolist(),
                                                  'ArbLevel': (
                                                          abs(sprTrade[locFail]) / (
                                                          self.notional * 2) - self.bidAskSpread).tolist()})
                    tempArbResult['Strike3'] = np.NaN
                    tempArbResult['Expiry'] = e
                    tempArbResult['Maturity'] = m
                    tempArbResult['Strat'] = 'Spread'
                    tempArbResult = tempArbResult[resultColumn]
                    arbFailutreDF = arbFailutreDF.append(tempArbResult)

                locFail = np.where(sprTradeCent > self.bidAskSpread * self.notional * 2)
                if (locFail[0].shape[0] > 0):
                    tempArbResult = pd.DataFrame(
                        {'Strike1': redCleansedVolData['Strike'].iloc[locLeft[locFail]].tolist(),
                         'Strike2': redCleansedVolData['Strike'].iloc[locRight[locFail]].tolist(),
                         'ArbLevel': (abs(sprTradeCent[locFail]) / (self.notional * 2) - self.bidAskSpread).tolist()})
                    tempArbResult['Strike3'] = np.NaN
                    tempArbResult['Expiry'] = e
                    tempArbResult['Maturity'] = m
                    tempArbResult['Strat'] = 'Spread-Centred'
                    tempArbResult = tempArbResult[resultColumn]
                    arbFailutreDF = arbFailutreDF.append(tempArbResult)

                locFail = np.where(secDeriv < -self.bidAskSpread * self.notional * 4)
                if (locFail[0].shape[0] > 0):
                    tempArbResult = pd.DataFrame({'Strike1': redCleansedVolData['Strike'].iloc[locFail].tolist(),
                                                  'Strike2': redCleansedVolData['Strike'].iloc[locFail[0] + 1].tolist(),
                                                  'Strike3': redCleansedVolData['Strike'].iloc[locFail[0] + 2].tolist(),
                                                  'ArbLevel': (
                                                          abs(secDeriv[locFail]) / (
                                                          self.notional * 4) - self.bidAskSpread).tolist()})
                    tempArbResult['Expiry'] = e
                    tempArbResult['Maturity'] = m
                    tempArbResult['Strat'] = 'Butterfly'
                    tempArbResult = tempArbResult[resultColumn]
                    arbFailutreDF = arbFailutreDF.append(tempArbResult)

                locFail = np.where(centButt < -self.bidAskSpread * self.notional * 4)
                if (locFail[0].shape[0] > 0):
                    tempArbResult = pd.DataFrame(
                        {'Strike1': redCleansedVolData['Strike'].iloc[locLeft[locFail]].tolist(),
                         'Strike3': redCleansedVolData['Strike'].iloc[locRight[locFail]].tolist(),
                         'ArbLevel': (abs(secDeriv[locFail]) / (self.notional * 4) - self.bidAskSpread).tolist()})

                    tempArbResult['Strike2'] = 0
                    tempArbResult['Expiry'] = e
                    tempArbResult['Maturity'] = m
                    tempArbResult['Strat'] = 'Butterfly-Centred'
                    tempArbResult = tempArbResult[resultColumn]
                    arbFailutreDF = arbFailutreDF.append(tempArbResult)

        arbFailutreDF['ArbLevel'] = arbFailutreDF['ArbLevel'] * 10000
        arbFailutreDF = arbFailutreDF.sort_values(by=['ArbLevel'], ascending=False)

        return arbFailutreDF


if __name__ == "__main__":

    try:
        allowParam = ['dir', 'fwd', 'ann', 'vol', 'bas']
        rootFolder = os.getcwd()  # '//SWPDV1/d$/IMBacktesting/Compilations/20180705_Arbitrage Free Swaption Vols/input/2018-08-03/USD/'
        parameter_dict = {}
        bidAskSpr = 0
        for user_input in sys.argv[1:]:  # Now we're going to iterate over argv[1:] (argv[0] is the program name)
            if "=" not in user_input:  # Then skip this value because it doesn't have the varname=value format
                continue
            varname = user_input.split("=")[0]  # Get what's left of the '='
            varvalue = user_input.split("=")[1]  # Get what's right of the '='
            if not varname in allowParam:
                print('Invalid parameter: You can only use dir, fwd, ann, vol and bas')
                raise Exception(varname)
            if varname == 'dir':
                rootFolder = varvalue
            elif varname == 'bas':
                bidAskSpr = float(varvalue)
            else:
                parameter_dict[varname] = varvalue

        arbObj = ArbChequer()
        if bidAskSpr > 0: arbObj = ArbChequer(bidAskSpread=bidAskSpr)
        assert arbObj.set_input_folder(folderPath=rootFolder,
                                       fileDic=parameter_dict), 'Wrong or non-existent Folder - Files'
        assert arbObj.load_files(), 'Something wrong with csv files'

        arbFailureDF = arbObj.runArbChecks()
        arbFailureDF.to_csv(arbObj.inputFolder + 'Arb_Report.csv', index=False)

    except Exception as e:
        print("Error: %s\n" % e.args[0])
