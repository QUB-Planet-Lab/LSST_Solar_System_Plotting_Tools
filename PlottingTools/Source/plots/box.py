from .plot import Plot
from seaborn import boxplot, boxenplot

class BoxPlot(Plot):
    def __init__(self, data, x, y, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        # box true return
        self.plot = boxplot(x = data[x], y = data[y])

class BoxenPlot(Plot):
    def __init__(self, data, x, y, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        # box true return
        self.plot = boxenplot(x = data[x], y = data[y])

    
 