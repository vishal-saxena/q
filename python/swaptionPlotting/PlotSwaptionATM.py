from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('ATM.pdf')

#cleansed
cleansed = pd.read_csv(
    "R:/Vishal.Saxena/SMART/Swaptions/alternative/RoadToRuinMar15/USD_Cleansed_VolCube.csv")

atmC = cleansed[cleansed['Strike'] == 0]
ax = plt.axes(projection='3d')

ax.set_title('ATM Cleansed X|Y|Z Expiry|Maturity|Vol');


ax.plot_trisurf(atmC["Expiry"], atmC["Maturity"], atmC["Vol"], linewidth=.1,cmap=cm.Blues)

pp.savefig()
# plt.show()
plt.close()

#smoothed
smoothed = pd.read_csv(
    "R:/Vishal.Saxena/SMART/Swaptions/alternative/RoadToRuinMar15/USD_ShapeChecked_VolCube.csv")

atmS = smoothed[smoothed['Strike'] == 0]

axS = plt.axes(projection='3d')


axS.plot_trisurf(atmS["Expiry"], atmS["Maturity"], atmS["Vol"], linewidth=.1,cmap=cm.Reds)

axS.set_title('ATM Smoothed X|Y|Z Expiry|Maturity|Vol');


pp.savefig()
# plt.show()
plt.close()


