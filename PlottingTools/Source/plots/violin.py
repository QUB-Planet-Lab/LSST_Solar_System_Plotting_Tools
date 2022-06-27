from .plot import Plot
#from seaborn import violinplot, set_theme, set
import seaborn as sns

class ViolinPlot(Plot):
    def __init__(self, data, x, y, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}):
        super().__init__(data, xlabel, ylabel, title, rc_params)        
        
        self.plot = sns.violinplot(x = data[x], y = data[y])