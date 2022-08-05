from .plot import Plot

import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import seaborn as sns

from typing import Optional, Literal

LIBRARIES = ['matplotlib', 'seaborn']



class HexagonalPlot(Plot):
    def __init__(self, data, x, y: Optional[str] = None, xbins : Optional[list] = None, ybins: Optional[list] = None, xlabel: str = "" , ylabel : str = "", title: str = "", colorbar : bool = True, library = 'seaborn', cache_data: Optional[bool] = False):
        super().__init__(data, xlabel, ylabel, title, library, cache_data)
            
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.fig.clear()

        sns.set_theme(style="ticks")
        self.plot = sns.jointplot(data = data, x = x , y = y, marginal_ticks=True, kind="hex", color = "blue")

        self.plot.ax_joint.set(xlabel = xlabel, ylabel = ylabel)

        self.fig = self.plot.figure
        self.fig.suptitle(title)
        self.ax = [self.plot.ax_joint, self.plot.ax_marg_x, self.plot.ax_marg_y]
        cbar_ax = self.plot.fig.add_axes([1, .25, .04, .5])

        plt.colorbar(cax=cbar_ax)

                            
            
class Histogram2D(Plot):
    def __init__(self, data, x, y: Optional[str] = None, xbins : Optional[list] = None, ybins: Optional[list] = None, xlabel: str = "" , ylabel : str = "", title: str = "", colorbar : bool = True, library = 'seaborn', cache_data: Optional[bool] = False, marginals : Optional[bool] = False, hex_plot: Optional[bool] = False):
        super().__init__(data, xlabel, ylabel, title, library, cache_data)

        self.fig.clear()

        if not marginals:
            self.plot = sns.histplot(data = data, x= x, y = y, cbar = colorbar)
            self.plot.set(xlabel = xlabel, ylabel = ylabel)
            self.fig = self.plot.figure

            self.fig.suptitle(title)


        else:
            sns.set_theme(style="ticks")

            self.plot = sns.JointGrid(data = data, x = x , y = y, marginal_ticks=True)
            #self.plot.set_axis_labels(xlabel = xlabel, ylabel = ylabel)

            self.plot.ax_joint.set_xlabel(xlabel)
            self.plot.ax_joint.set_ylabel(ylabel)

            # Set a log scaling on the y axis
            #g.ax_joint.set(yscale="log")

            # Create an inset legend for the histogram colorbar
            cax = self.plot.figure.add_axes([1, .25, .04, .5])

            # Add the joint and marginal histogram plots
            self.plot.plot_joint(
                sns.histplot, discrete=(False, False),
                cmap="light:#03012d", pmax=.8, cbar=True, cbar_ax=cax
            )
            self.plot.plot_marginals(sns.histplot, color="#03012d")
            self.fig = self.plot.figure
            self.ax = [self.plot.ax_joint, self.plot.ax_marg_x, self.plot.ax_marg_y]

            self.fig.suptitle(title)
    
    
class HistogramPlot(Plot):
    def __init__(self, data, x, y = None, xbins : Optional[list] = None, ybins: Optional[list] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}, projection : Literal['1d', '2d', '2d_hex'] = '1d', colorbar : bool = True, library = 'seaborn', cache_data: Optional[bool] = False):
        super().__init__(data, xlabel, ylabel, title, library, cache_data)
        
        if library not in LIBRARIES:
            raise Exception(f"{library} is not a valid option for library. Valid options include {LIBRARIES}")
            
        self.library = library
    
        if projection == '1d':
            if self.library == "seaborn":
                self.plot = sns.histplot(data = data, x = x, ax = self.ax)
                self.plot.set(xlabel = None, ylabel = None)
            else:
                self.plot = self.ax.hist(x = data[x], bins = xbins, edgecolor="white")
        
        if projection == '2d':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")

            
            if self.library == "seaborn":
                self.fig.clear()
                self.plot = sns.histplot(data = data, x= x, y = y, cbar = colorbar)
                self.plot.set(xlabel = xlabel, ylabel = ylabel)
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
                self.fig.clear()
                self.plot = sns.jointplot(data = data, x = x, y = y, kind="hex")
                #self.plot.set(xlabel = None, ylabel = None)
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
            
            
                        