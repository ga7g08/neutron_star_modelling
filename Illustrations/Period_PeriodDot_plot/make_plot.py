import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc_file
import pandas as pd
import sys

rc_file("/home/greg/Neutron_star_modelling/matplotlibrc")

DATA_FILE = sys.argv[1] #"name_p0_p1_AGE_BSURF_PB.txt"

data = np.genfromtxt(DATA_FILE, skip_header=4, skip_footer=1)

df = pd.DataFrame({'p0' : data[:, 0],
                   'p1' : data[:, 1],
                   'BSURF' : data[:, 3],
                   'PB' : data[:, 4]
                  })

fig = plt.figure(figsize=(6,8))
ax = fig.add_subplot(111)



# Normal pulsars
normal_df = df[(df.p0 > 1e-1) & (df.p1 > 0) & (df.PB.isnull())]
ax.scatter(normal_df.p0.values, normal_df.p1.values,
           s = 10, c='k', marker="o", label="Normal pulsars")

# Millisecond pulsars
MSP_df = df[(df.p0 < 1e-1) & (df.p1 < 1e-16) & (df.PB.isnull())]
ax.scatter(MSP_df.p0.values, MSP_df.p1.values,
           s = 20, c="k", facecolors="none", edgecolors="k", 
           marker="o", label="MSP")

# Binary MSP pulars
binary_MSP_df = df[~(df.PB.isnull()) & (df.p0 < 1e-1)]
ax.scatter(binary_MSP_df.p0.values, binary_MSP_df.p1.values,
           s = 20, facecolors='r', edgecolors="k",
           marker="o", label="Binary MSP")

# Binary normal pulars
binary_normal_df = df[~(df.PB.isnull()) & (df.p0 > 1e-1)]
ax.scatter(binary_normal_df.p0.values, binary_normal_df.p1.values,
           s = 20, facecolors='b', edgecolors="k",
           marker="o", label="Binary pulsars")

# Magnetars
magnetar_df = df[(df.BSURF > 5e13)]
ax.scatter(magnetar_df.p0.values, magnetar_df.p1.values,
           s = 40, c='r', marker="2", label="Magnetars")

P_range = np.logspace(-4, 2, 100)
## Add lines of constant magnetic field
def Pdot(P, B0):
    CONST = 3.2e19
    return (B0 / CONST) ** 2 / P  
B0s = np.logspace(10, 16, 7)
text_X = 1e1
for B0 in B0s:
    power = np.log10(B0)
    if power != int(power):
        print "pow = {} is not an int".format(power)
    ax.text(text_X, 0.8*Pdot(text_X, B0), 
            "$B_{{0}}=$" + "$10^{{{}}}$".format(int(power)),
            rotation=-35.3,            
            bbox=dict(facecolor='w', alpha=0.8, edgecolor="w")
            )
    ax.plot(P_range, Pdot(P_range, B0), ls="--", 
            lw=0.5, color="k")

# Add lines of constant characteristic age
def Pdot(P, tau):
    return 0.5 * P/tau 
tau_years = np.logspace(1, 9, 9)
text_X = 2e-4
for tau_year in tau_years:
    tau = tau_year * (365. * 86400)
    rotation=28
    power = np.log10(tau_year)
    if power != int(power):
        print "pow = {} is not an int".format(power)
    ax.text(text_X, 2.5*Pdot(text_X, tau), 
            r"$\tau=$" + "$10^{{{}}}$".format(int(power)),
            rotation=rotation,
            bbox=dict(facecolor='w', alpha=0.8, edgecolor="w")
            )
    ax.plot(P_range, Pdot(P_range, tau), ls="--", 
            color="k", lw=0.5)

# Add the DEATH LINE
#CONST = 1e-16
#ax.plot(P_range, CONST * P_range, ls="-", color="r")

ax.legend(loc=4, frameon=True, fontsize=12, numpoints=1)
ax.set_xlabel("Period [s]")
ax.set_ylabel("Period deviative")


xlims = (1e-4, 200)
ax.set_xlim(*xlims)
ax.set_ylim(1e-22, 1e-7)

ax.set_xscale('log')
ax.set_yscale('log')

#plt.savefig("Period_PeriodDot.pdf")
plt.show()