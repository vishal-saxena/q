from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

vs = pd.read_csv(
    "D:/home/vishal/git_proj/smart-swaptions/swaptions-core/src/test/resources/steffen/rebaseLine/bloomberg/usd/smoothing/USD_ShapeChecked_VolCube.csv")
atm = vs[vs['Strike'] == 0]

fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_trisurf(atm["Expiry"], atm["Maturity"], atm["Vol"], cmap=cm.jet, linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.savefig('atm.pdf')
plt.show()
