"""
"""
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import os

os.chdir('/Users/katiepelton/Desktop/urban-aq/nmf/data')

# force the math text to look normal
mpl.rcParams['mathtext.default'] = 'regular'

def major_ticks(x, pos=None):
    """Set the major ticks according 
    to this custom style
    """
    x = mdates.num2date(x)
    if pos == 0:
        fmt = "%-d\n%b %Y\n%I %p"
    else:
        fmt = "%-d"
    return x.strftime(fmt)

# set the default seaborn params
sns.set("paper", "ticks", color_codes=True, palette='colorblind')

# load the timeseries data
ts = pd.read_feather('timeseries-results.feather').set_index("timestamp_iso")

# load the composition data
comp = pd.read_feather('composition-results.feather')

# # load the bootstrapped results
bs = pd.read_feather('bootstrap.feather')

# set up the figure
fig = plt.figure(figsize=(9, 3))

# build a gridspec-based layout
gs = fig.add_gridspec(1, 5)

ax1 = fig.add_subplot(gs[0, 0:2])
ax2 = fig.add_subplot(gs[0, 2:])

# Plot the timeseries
cols_to_plot = [col for col in ts.columns if "Factor" in col]

# resample the data so we don't have any gaps!
# ts2 = ts[: snakemake.config['plt_tf']].resample('5min').mean()[cols_to_plot]
# if ts2.shape[0] == 0:
#     ts2 = ts.iloc[0:5000].resample('5min').mean()[cols_to_plot]

ts2 = ts

# plot the time series data
ax2.plot(ts2[cols_to_plot[0]], lw=3, color=sns.xkcd_rgb['greyish'])
ax2.plot(ts2[cols_to_plot[1]], lw=3, color=sns.xkcd_rgb['faded green'])
ax2.plot(ts2[cols_to_plot[2]], lw=3, color=sns.xkcd_rgb['dusty purple'])

# remove ticks on y axis
ax2.set_ylim(0, None)
ax2.set_xlim(ts2.index[0], ts2.index[-1])
ax2.set_ylabel("Factor Intensity (a.u.)")
ax2.legend([
    "Factor 1 (CO-dominated)",
    "Factor 2 (Particle Factor 1)",
    "Factor 3 (Particle Factor 2)"
], loc="upper right")

# set the xaxis labels (timestamps) on fig 2a
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax2.xaxis.set_major_formatter(FuncFormatter(major_ticks))
ax2.xaxis.set_minor_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))

# remove the spine
sns.despine()

# ################
# #### Figure 2a #
# ################
cols = ['co2', 'co', 'no2', 'o3', 'pm1', 'pm25', 'pm10']

pal = sns.color_palette()

colors = [pal[3], pal[2], pal[4], pal[5]]
colors += sns.color_palette("Blues_r", 3)

ax1 = sns.barplot(
    data=bs,
    x="variable", y="value", hue='index', ax=ax1, hue_order=cols, ci="sd",
    palette=colors, saturation=1, edgecolor='black', linewidth=0.25,
    errwidth=.75,
)

ax1.set_ylim(0, 1)
ax1.set_xlabel("")
ax1.set_ylabel("Percent of Species Signal\nDescribed by Factor", fontsize=11)
ax1.set(yticks=np.linspace(0, 1, 11), yticklabels=["0","","","","","50","","","","","100"])

handles, _ = ax1.get_legend_handles_labels()
# labels = ["CO", "$O_3$", "$SO_2$", "$NO_2$", "Bin 0", "Bin 1", "Bin 2"]
labels = ['co2', 'co', 'no2', 'o3', 'pm1', 'pm25', 'pm10']
ax1.legend(handles, labels, bbox_to_anchor=(1.3, 0.9))

# make the plots a bit shorter to make room for the figure sub-labels
plt.subplots_adjust(top=.5)

# add some figure text
plt.gcf().text(0.09, 0.9, "(a)", fontsize=12)
plt.gcf().text(0.5, 0.9, "(b)", fontsize=12)

plt.tight_layout()

fig.savefig('figure', dpi=350)