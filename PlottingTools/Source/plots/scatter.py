from .plot import Plot
import seaborn as sns
import matplotlib.pyplot as plt

from typing import Optional, Literal


LIBRARIES = ['matplotlib', 'seaborn']



class ScatterPlot(Plot):
    """Helper object for creating plots"""
    
    def __init__(self, data, x, y, z : Optional[str] = None, xlabel: str = "" , ylabel : str = "", title: str = "", yerr = [], xerr = [], rc_params : dict = {}, projection: Optional[Literal['2d', '3d']] = '2d', library : Optional[str] = 'seaborn'):
        """
            :param data
            :param: x, value to be plotted on x scale
        """
        
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        if library not in LIBRARIES:
            raise Exception(f"{library} is not a valid option for library. Valid options include {LIBRARIES}")
        print(library)
        self.library = library
        
        if projection == '2d':
            if library == "seaborn":
                self.plot = sns.scatterplot(data = data, x = x, y = y)
            else:
                if len(yerr) or len(xerr):
                    self.plot = self.ax.errorbar(x = data[x], y = data[y], yerr=yerr if len(yerr) else None, xerr=xerr if len(xerr) else None, fmt='o')
                self.plot = self.ax.scatter(x = data[x], y = data[y])
            
        elif projection == '3d':
            if library == "seaborn":
                print("Seaborn not available in 3d, reverting to matplotlib")
            self.fig.clear()
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(projection="3d")
            self.plot = self.ax.scatter(xs = data[x], ys = data[y], zs = data[z])
            