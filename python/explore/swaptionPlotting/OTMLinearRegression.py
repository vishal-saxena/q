from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from matplotlib.backends.backend_pdf import PdfPages

import matplotlib.patches as mpatches

red_dots = mpatches.Patch(color='red', label='smoothed')
blue_dots = mpatches.Patch(color='blue', label='cleansed')
grey_line = mpatches.Patch(color='grey', label='murex - smoothed int/ext polated -990:+990:10bps')
orange_line = mpatches.Patch(color='orange', label='OLS cubic')
green_dots = mpatches.Patch(color='green', label='Missing or < reqd. num contribs on pricing grid')
pink_dots = mpatches.Patch(color='pink', label='delta +(cleansed) x(flattened vol)')
cyan_dots = mpatches.Patch(color='cyan', label='vega +(cleansed) x(monotonic breach fixed)')


pp = PdfPages('OTM-OLS_Cubic-CNN_NomuraJun12.pdf')


def OTMLinearRegression3(expiry, maturity, cleansed, smoothed, murex):
    print("Plotting %s-%s" % (expiry, maturity))

    # OTM
    plt.title("Expiry-Maturity(Days): %s-%s" % (expiry, maturity))
    plt.xlabel("RelativeStrike (Bps)")
    plt.ylabel("Vol (Bps)")

    plt.legend(handles=[green_dots, blue_dots, pink_dots,cyan_dots,red_dots, grey_line, orange_line])

    otm = cleansed.loc[(cleansed['Expiry'] == expiry) & (cleansed['Maturity'] == maturity)]
    smile = otm.iloc[:, [2, 3]]
    present = smile[smile["Vol"] != -1]
    x = present["Strike"]
    y = present["Vol"]
    xfit = np.arange(-990, 1000, 10)

    # Linear
    # linear = linear_model.LinearRegression()
    # linear.fit(x[:, np.newaxis], y)
    # yfit = linear.predict(xfit[:, np.newaxis])
    # plt.plot(xfit, yfit);

    # OTM cleansed
    plt.scatter(x, y, c="Blue")

    # OTM cleansed pricing grid
    missing = smile[smile["Vol"] == -1]
    missingX = missing["Strike"]
    missingY = missing["Vol"]

    plt.scatter(missingX, missingY, c="Green")

    # OLS Cubic
    poly_model = make_pipeline(PolynomialFeatures(3),
                               LinearRegression())
    poly_model.fit(x[:, np.newaxis], y)
    yPfit = poly_model.predict(xfit[:, np.newaxis])
    plt.plot(xfit, yPfit, c="Orange");

    # OTM smoothed

    otmSmoothed = smoothed.loc[(smoothed['Expiry'] == expiry) & (smoothed['Maturity'] == maturity)]
    smileSmoothed = otmSmoothed.iloc[:, [2,3,4,5,6,7]]
    xSmoothed = smileSmoothed["Strike"]
    ySmoothed = smileSmoothed["Vol"]
    deltas = smileSmoothed["Deltas"]
    subsVolsDelta = smileSmoothed["SubsVolDeltas"]
    vegas = smileSmoothed["Vegas"]
    subsVolsVegas = smileSmoothed["SubsVolVegas"]

    plt.scatter(xSmoothed, ySmoothed, facecolors='none', edgecolors='Red')

    # OTM murex

    otmMurex = murex.loc[(murex['Expiry'] == expiry) & (murex['Maturity'] == maturity)]
    smileMurex = otmMurex.iloc[:, [2, 3]]
    xMurex = smileMurex["Strike"]
    yMurex = smileMurex["Vol"]
    plt.scatter(xMurex, yMurex, c="Black", alpha=.1)

    #OTM greeks used in smoothing
    deltaAxis = plt.twinx()
    deltaAxis.spines['left'].set_position(('outward', 12))
    deltaAxis.set_ylabel("Delta",color ="Pink")

    deltaAxis.scatter(xSmoothed, deltas, c="Pink", marker='+')
    deltaAxis.scatter(xSmoothed, subsVolsDelta, c="Pink", marker='x')

    vegaAxis = plt.twinx()
    vegaAxis.set_ylabel("Vega", color="Cyan")
    vegaAxis.spines['right'].set_position(('outward', 12))

    vegaAxis.scatter(xSmoothed, vegas, c="Cyan", marker ='+')
    vegaAxis.scatter(xSmoothed, subsVolsVegas, c="Cyan", marker ='x')


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

cleansedVolCubeFilePath = "R:/Vishal.Saxena/SMART/Swaptions/alternative/CNNNomuraCombined_QC1592/USD_Cleansed_PricingGrid_VolCube.csv"
smoothedVolCubeFilePath = "R:/Vishal.Saxena/SMART/Swaptions/alternative/CNNNomuraCombined_QC1592/USD_ShapeChecked_VolCube.csv"
murexVolCubeFilePath = "R:/Vishal.Saxena/SMART/Swaptions/alternative/CNNNomuraCombined_QC1592/MurexCubeVolCube.csv"

# data
cleansed = pd.read_csv(
    cleansedVolCubeFilePath)

smoothed = pd.read_csv(
    smoothedVolCubeFilePath)

murex = pd.read_csv(
    murexVolCubeFilePath)

# ATM Cleansed

atmC = cleansed[cleansed['Strike'] == 0]
ax = plt.axes(projection='3d')
ax.set_xlabel("Expiry (Days)")
ax.set_ylabel("Maturity (Days)")
ax.set_zlabel("Vol (bps)")
# ax.set_title('ATM Cleansed X|Y|Z Expiry|Maturity|Vol');
# ax.plot_trisurf(atmC["Expiry"], atmC["Maturity"], atmC["Vol"], linewidth=.1, cmap=cm.Blues)
cleansedScatter = ax.scatter3D(atmC["Expiry"], atmC["Maturity"], atmC["Vol"],'blue')
# pp.savefig()
# plt.close()

# ATM Smoothed
atmS = smoothed[smoothed['Strike'] == 0]
# axS = plt.axes(projection='3d')
# axS.plot_trisurf(atmS["Expiry"], atmS["Maturity"], atmS["Vol"], linewidth=.1, cmap=cm.Reds)
# axS.set_title('ATM Smoothed X|Y|Z Expiry|Maturity|Vol');
smoothScatter = ax.scatter3D(atmS["Expiry"], atmS["Maturity"], atmS["Vol"],facecolors='none', edgecolors='r')

ax.legend((cleansedScatter,smoothScatter),('Cleansed','Smoothed'))
pp.savefig()
plt.close()

for eidx, e in enumerate(expiries):
    for midx, m in enumerate(maturities):
        OTMLinearRegression3(e, m,
                             cleansed,
                             smoothed,
                             murex
                             )
