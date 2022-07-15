from .plot import Plot

import matplotlib.pyplot as plt
from typing import Optional, Literal

#add 2d histogram here

class HistogramPlot(Plot):
    def __init__(self, data, x, y: Optional[str] = None,xbins : Optional[list] = None, ybins: Optional[list] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}, projection : Literal['1d', '2d', '2d_hex'] = '1d'):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        if projection == '1d':
            self.plot = self.ax.hist(x = data[x], bins = xbins, edgecolor="white")
        
        if projection == '2d':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")
            self.plot = self.ax.hist2d(x = data[x], y=data[y])
            
        if projection == '2d_hex':
            if not y:
                raise Exception("Y values must be provided when using a 2d histogram")
            self.plot = self.ax.hexbin(x = data[x], y=data[y])
            