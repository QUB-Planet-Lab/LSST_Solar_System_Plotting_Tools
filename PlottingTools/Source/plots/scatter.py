from .plot import Plot
from seaborn import scatterplot

class ScatterPlot(Plot):
    def __init__(self, data, x, y, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        self.plot = scatterplot(x = data[x], y = data[y], s=2)
       
