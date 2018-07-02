import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model

cleansed = pd.read_csv(
    "D:/home/vishal/git_proj/smart-swaptions/swaptions-core/src/test/resources/clsg/expected/cleansing/USD_Cleansed_VolCube.csv")
otm = cleansed.loc[(cleansed['Expiry'] == 365) & (cleansed['Maturity'] == 365)]
smile = otm.iloc[:, [2, 3]]
x = smile["Strike"]
y = smile["Vol"]
xfit = np.arange(-990, 1000, 10)
linear = linear_model.LinearRegression()
linear.fit(x[:, np.newaxis], y)
yfit = predicted = linear.predict(xfit[:, np.newaxis])
plt.scatter(x, y, c="Blue")
plt.plot(xfit, yfit);

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

poly_model = make_pipeline(PolynomialFeatures(3),
                           LinearRegression())
poly_model.fit(x[:, np.newaxis], y)
yPfit = poly_model.predict(xfit[:, np.newaxis])
plt.plot(xfit, yPfit, c="Orange");

smoothed = pd.read_csv(
    "D:/home/vishal/git_proj/smart-swaptions/swaptions-core/src/test/resources/clsg/expected/smoothing/USD_ShapeChecked_VolCube.csv")
otmSmoothed = smoothed.loc[(smoothed['Expiry'] == 365) & (smoothed['Maturity'] == 365)]
smileSmoothed = otmSmoothed.iloc[:, [2, 3]]
xSmoothed = smileSmoothed["Strike"]
ySmoothed = smileSmoothed["Vol"]
plt.scatter(xSmoothed, ySmoothed, c="Red")

murex = pd.read_csv(
    "D:/home/vishal/git_proj/smart-swaptions/swaptions-core/src/test/resources/clsg/expected/smoothing/MurexCubeVolCube.csv")
otmMurex = murex.loc[(murex['Expiry'] == 365) & (murex['Maturity'] == 365)]
smileMurex = otmMurex.iloc[:, [2, 3]]
xMurex = smileMurex["Strike"]
yMurex = smileMurex["Vol"]
plt.scatter(xMurex, yMurex, c="Black")

goodnessPerc = np.abs((yPfit - yMurex)/yPfit)
goodnessAbs=np.abs(yPfit - yMurex)
print(np.max(goodnessPerc))
print(np.max(goodnessAbs))
from scipy.stats import chisquare
cs = chisquare(yPfit, yMurex)
print (cs)

# plt.show()

# otmMPlus = cleansed.loc[(cleansed['Expiry'] == 3650) & (cleansed['Maturity'] == 4380)]
# otmMPlusSmile = otmMPlus.iloc[:, [2, 3]]
# yMPlus=otmMPlusSmile["Vol"]
# xBi= np.array([x,yMPlus])

# poly_model_Bi = make_pipeline(PolynomialFeatures(2),
#                            LinearRegression())
# poly_model_Bi.fit(xBi[:, np.newaxis], y)
# yPBifit = poly_model_Bi.predict(xfit[:, np.newaxis])
# plt.plot(xfit, yPBifit,c="Purple");

# poly = PolynomialFeatures(degree=2)
# xBi_ = poly.fit_transform(xBi)
# xfit_ = poly.fit_transform(xfit)
# clf = linear_model.LinearRegression()
# clf.fit(xBi_, y)
# clf.predict(xfit_)


