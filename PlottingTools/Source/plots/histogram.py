from .plot import Plot

import matplotlib.pyplot as plt
from typing import Optional

#add 2d histogram here

class HistogramPlot(Plot):
    def __init__(self, data, x, xbins, y: Optional[str] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        
        self.plot = self.ax.hist(x = data[x], bins = xbins, edgecolor="white")