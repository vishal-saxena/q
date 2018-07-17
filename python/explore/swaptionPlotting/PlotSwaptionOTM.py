
import matplotlib.pyplot as plt
import pandas as pd


vs = pd.read_csv(
    "D:/home/vishal/git_proj/smart-swaptions/swaptions-core/src/test/resources/steffen/rebaseLine/bloomberg/usd/smoothing/USD_ShapeChecked_VolCube.csv")
otm = vs.loc[(vs['Expiry'] == 3650) & (vs['Maturity'] == 3650)]
smile = otm.iloc[:, [2, 3]]

# smile.plot.scatter(x='Strike', y='Vol',c='DarkBlue')
# plt.show()

fig = plt.figure()
ax = fig.add_subplot(111)
line = ax.plot(smile["Strike"], smile["Vol"], color="DarkBlue")
plt.savefig('otm.pdf')
plt.show()
