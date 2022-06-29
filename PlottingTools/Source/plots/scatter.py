from .plot import Plot
from seaborn import scatterplot

class ScatterPlot(Plot):
    """Helper object for creating plots"""
    
    def __init__(self, data, x, y, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}):
        """
            :param data
            :param: x, value to be plotted on x scale
        """
        super().__init__(data, xlabel, ylabel, title, rc_params)
        self.plot = scatterplot(x = data[x], y = data[y], s=2)
       
