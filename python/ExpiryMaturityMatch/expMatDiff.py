import pandas as pd
import os
import datetime
import numpy as np

dateparseSmart = lambda x: pd.datetime.strptime(x, '%d/%m/%Y')
dateparseRon = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

if __name__ == "__main__":
    rec_dir = "D:/home/vishal/temp/swaptions/expMatRec1/"

    ronExpMatAllDates = pd.read_csv(rec_dir + "/" + "tradeDate_expTenor_matTenor_to_dates_small - Copy.csv",
                                    parse_dates=['exp_date', 'mat_date'], date_parser=dateparseRon)
    ronExpMatAllDates = ronExpMatAllDates.loc[
        (ronExpMatAllDates['mat_tenor'] != "18M") & (ronExpMatAllDates['ccy'] == "USD")]
    ronExpMatAllDates = ronExpMatAllDates[["date", "exp_tenor", "mat_tenor", "exp_date", "mat_date", ]]

    smart_dir = rec_dir + "/" + "usd" + "/" + "smart"
    resulst_dir = rec_dir + "/" + "usd" + "/" + "results"
    dates = []
    recAllDates = pd.DataFrame()
    for f in os.listdir(smart_dir):
        date = f[:8]
        ronDate = datetime.datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
        dates.append(ronDate)
        smart_expMat_file = os.path.abspath(os.path.join(smart_dir + "/", f))
        smartExpMat = pd.read_csv(smart_expMat_file, parse_dates=['ExpiryDate', 'MaturityDate'],
                                  date_parser=dateparseSmart)

        smartExpMat = smartExpMat.loc[smartExpMat['Strike'] == 0]
        smartExpMat = smartExpMat[["ExpiryLabel", "MaturityLabel", "ExpiryDate", "MaturityDate"]]

        ronExpMat = ronExpMatAllDates.loc[ronExpMatAllDates["date"] == ronDate]
        valuationDateCol = ronExpMat['date']
        ronExpMat = ronExpMat.loc[:, ronExpMat.columns != 'date']
        ronExpMat.columns = ["ExpiryLabel", "MaturityLabel", "ExpiryDate", "MaturityDate"]

        combined = pd.merge(smartExpMat, ronExpMat, on=["ExpiryLabel", "MaturityLabel"])

        combined["ExpiryDiff"] = combined.iloc[:, 2] == combined.iloc[:, 4]
        combined["MaturityDiff"] = combined.iloc[:, 3] == combined.iloc[:, 5]

        if (ronExpMat.shape == smartExpMat.shape):
            combined.insert(0, 'ValuationDate', date)
            combined.to_csv(os.path.abspath(os.path.join(rec_dir + "/" + date + "_rec.csv")))
            print("Reconciled for %s", date)
        else:
            print("Won't reconcile for %s as smartExpMat shape %s different to ronExpMat shape %s", date,
                  smartExpMat.shape, ronExpMat.shape)

        recAllDates = recAllDates.append(combined)
        # recAllDates = pd.concat([recAllDates, combined], axis=0)
    recAllDates.to_csv(os.path.abspath(os.path.join(rec_dir + "/" + "AllDates_rec.csv")))
    print(dates)
