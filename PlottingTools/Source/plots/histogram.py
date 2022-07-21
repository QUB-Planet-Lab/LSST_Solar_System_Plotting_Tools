from .plot import Plot

import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import seaborn as sns

from typing import Optional, Literal

LIBRARIES = ['matplotlib', 'seaborn']


    
class HistogramPlot(Plot):
    def __init__(self, data, x, y: Optional[str] = None, xbins : Optional[list] = None, ybins: Optional[list] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}, projection : Literal['1d', '2d', '2d_hex'] = '1d', colorbar : bool = True, library = 'seaborn'):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        if library not in LIBRARIES:
            raise Exception(f"{library} is not a valid option for library. Valid options include {LIBRARIES}")
            
        self.library = library
    
        if projection == '1d':
            if self.library == "seaborn":
                self.plot = sns.histplot(data = data, x = x)
            else:
                self.plot = self.ax.hist(x = data[x], bins = xbins, edgecolor="white")
        
        if projection == '2d':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")

            # TO-DO create dynamic sizing of plots
            
            if self.library == "seaborn":
                self.plot = sns.histplot(data = data, x= x, y = y, cbar = colorbar)
            else:
                self.fig.clear()
                self.fig = plt.figure(figsize=(8, 8))
                gs = self.fig.add_gridspec(
                    2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05
                )
                self.ax = self.fig.add_subplot(gs[1, 0])
                ax_histx = self.fig.add_subplot(gs[0,0], sharex=self.ax)
                ax_histy = self.fig.add_subplot(gs[1,1], sharey=self.ax)
                ax_histx.tick_params(axis="x", labelbottom=False)
                ax_histy.tick_params(axis="y", labelleft=False)


                self.ax.hist2d(data[x], data[y])

                ax_histx.hist(data[x], edgecolor="white", color="black")
                ax_histx.spines.top.set_visible(False)
                ax_histx.spines.right.set_visible(False)

                ax_histx.set_ylabel("Count")

                ax_histy.hist(data[y], edgecolor="white", color="black", orientation='horizontal')


                ax_histy.spines.top.set_visible(False)
                ax_histy.spines.right.set_visible(False)

                ax_histy.set_xlabel("Count")
            
        if projection == '2d_hex':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")
            if library == "seaborn":
                self.plot = sns.jointplot(data = data, x = x, y = y ,kind="hex")
            else:
            #self.plot = self.ax.hexbin(x = data[x], y=data[y])
                self.fig.clear()
                self.fig = plt.figure(figsize=(8, 8))
                gs = self.fig.add_gridspec(
                    2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05
                )
                self.ax = self.fig.add_subplot(gs[1, 0])

                if colorbar:
                    self.fig.colorbar(ScalarMappable(), ax = self.ax, pad=0.01)

                ax_histx = self.fig.add_subplot(gs[0,0], sharex=self.ax)
                ax_histy = self.fig.add_subplot(gs[1,1], sharey=self.ax)
                ax_histx.tick_params(axis="x", labelbottom=False)
                ax_histy.tick_params(axis="y", labelleft=False)


                self.ax.hexbin(data[x], data[y])

                ax_histx.hist(data[x], edgecolor="white", color="black")

                ax_histx.spines.top.set_visible(False)
                ax_histx.spines.right.set_visible(False)

                ax_histx.set_ylabel("Count")

                ax_histy.hist(data[y], edgecolor="white", color="black", orientation='horizontal')


                ax_histy.spines.top.set_visible(False)
                ax_histy.spines.right.set_visible(False)

                ax_histy.set_xlabel("Count")
            
            
                        