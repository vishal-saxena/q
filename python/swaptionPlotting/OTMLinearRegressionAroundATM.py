import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('OTMLinearRegressionCubic.pdf')

def OTMLinearRegression3(expiry, maturity, cleansedVolCubeFilePath, smoothedVolCubeFilePath,murexVolCubeFilePath):

    plt.title("%s-%s" %(expiry,maturity))

    cleansed = pd.read_csv(
        cleansedVolCubeFilePath)

    otm = cleansed.loc[(cleansed['Expiry'] == expiry) & (cleansed['Maturity'] == maturity)]
    smile = otm.iloc[:, [2, 3]]
    x = smile["Strike"]
    y = smile["Vol"]
    xfit = np.arange(-290, 1000, 10)

    # Linear
    # linear = linear_model.LinearRegression()
    # linear.fit(x[:, np.newaxis], y)
    # yfit = linear.predict(xfit[:, np.newaxis])
    # plt.plot(xfit, yfit);

    plt.scatter(x, y, c="Blue")

    poly_model = make_pipeline(PolynomialFeatures(3),
                               LinearRegression())
    poly_model.fit(x[:, np.newaxis], y)
    yPfit = poly_model.predict(xfit[:, np.newaxis])
    plt.plot(xfit, yPfit, c="Orange");

    smoothed = pd.read_csv(
        smoothedVolCubeFilePath)

    otmSmoothed = smoothed.loc[(smoothed['Expiry'] == expiry) & (smoothed['Maturity'] == maturity)]
    smileSmoothed = otmSmoothed.iloc[:, [2, 3]]
    xSmoothed = smileSmoothed["Strike"]
    ySmoothed = smileSmoothed["Vol"]
    plt.scatter(xSmoothed, ySmoothed, c="Red")

    murex = pd.read_csv(
        murexVolCubeFilePath)

    otmMurex = murex.loc[(murex['Expiry'] == expiry) & (murex['Maturity'] == maturity)]
    smileMurex = otmMurex.iloc[:, [2, 3]]
    xMurex = smileMurex["Strike"]
    yMurex = smileMurex["Vol"]
    plt.scatter(xMurex, yMurex, c="Black")

    pp.savefig()

    plt.close()

    # yPFitAroundATM = yPfit[80:120]
    # yMurexAroundATM = yMurex[80:120]
    # goodnessPerc = np.abs((yPFitAroundATM - yMurexAroundATM) / yMurexAroundATM)
    # goodnessAbs = np.abs(yPFitAroundATM - yMurexAroundATM)
    # print("Expiry:%s Maturity:%s PercentageOutage:%s AbsOutage:%s" % (
    #     expiry, maturity, np.max(goodnessPerc), np.max(goodnessAbs)))


expiries = np.array(
    [1, 7, 14, 30, 90, 180, 270, 365, 540, 730, 1095, 1460, 1825, 2190, 2555, 2920, 3285, 3650, 4380, 5475, 7300,
     10950])
maturities = np.array([365, 730, 1095, 1460, 1825, 2190, 2555, 2920, 3285, 3650, 4380, 5475, 7300, 9125, 10950])
# fig, axs = plt.subplots(22, 15, sharex=True, sharey=True)

for eidx, e in enumerate(expiries):
    for midx, m in enumerate(maturities):



        #     axs[eidx, midx]
        # axsidx.set(title=("%s-%s" %(e,m)))
        OTMLinearRegression3(e, m,
                             "R:/Vishal.Saxena/SMART/Swaptions/alternative/RoadToRuinMar15/USD_Cleansed_VolCube.csv",
                             "R:/Vishal.Saxena/SMART/Swaptions/alternative/RoadToRuinMar15/USD_ShapeChecked_VolCube.csv",
                             "R:/Vishal.Saxena/SMART/Swaptions/alternative/RoadToRuinMar15/MurexCubeVolCube.csv",
                             )

# plt.show()
# plt.savefig("OTMLinearRegressionCubic.pdf")
