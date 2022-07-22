from .plot import Plot
import seaborn as sns
import matplotlib.pyplot as plt

from typing import Optional, Literal


LIBRARIES = ['matplotlib', 'seaborn']

class ScatterPlot(Plot):
    """Helper object for creating plots"""
    
    def __init__(self, data, x, y, z : Optional[str] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], projection: Optional[Literal['2d', '3d']] = '2d', library : Optional[str] = 'seaborn'): # rc_params : dict = {}
        """
            :param data
            :param: x, value to be plotted on x scale
        """
        
        super().__init__(data, xlabel, ylabel, title, library) #rc_params
        
        if library not in LIBRARIES:
            raise Exception(f"{library} is not a valid option for library. Valid options include {LIBRARIES}")
            

        
        if projection == '2d':
            if len(yerr) or len(xerr):
                if library == "seaborn":
                    print("Error bars not available with seaborn reverting to matplotlib")
                self.plot = self.ax.errorbar(x = data[x], y = data[y], yerr=yerr if len(yerr) else None, xerr=xerr if len(xerr) else None, fmt='o')
            else:
                if library == "seaborn":
                    self.plot = sns.scatterplot(data = data, x = x, y = y, ax = self.ax).set(xlabel=None, ylabel = None)
                else:
                    self.plot = self.ax.scatter(x = data[x], y = data[y])

        elif projection == '3d':
            if library == "seaborn":
                print("Seaborn not available in 3d, reverting to matplotlib")
            self.fig.clear()
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(projection="3d")
            self.plot = self.ax.scatter(xs = data[x], ys = data[y], zs = data[z])
            