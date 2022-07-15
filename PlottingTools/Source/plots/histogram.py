from .plot import Plot

import matplotlib.pyplot as plt
from typing import Optional, Literal

#add 2d histogram here


def chart(x, y, ax, ax_histx, ax_histy):
    # no labels
    pass

    
    
class HistogramPlot(Plot):
    def __init__(self, data, x, y: Optional[str] = None,xbins : Optional[list] = None, ybins: Optional[list] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}, projection : Literal['1d', '2d', '2d_hex'] = '1d'):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        if projection == '1d':
            self.plot = self.ax.hist(x = data[x], bins = xbins, edgecolor="white")
        
        if projection == '2d':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")
            #self.plot = self.ax.hist2d(x = data[x], y=data[y])
            # TO-DO create dynamic sizing of plots
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

            ax_histx.hist(data[x])
            ax_histy.hist(data[y], orientation='horizontal')
            
        if projection == '2d_hex':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")
            #self.plot = self.ax.hexbin(x = data[x], y=data[y])
            
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

    
            self.ax.hexbin(data[x], data[y])

            ax_histx.hist(data[x])
            ax_histy.hist(data[y], orientation='horizontal')
            