import seaborn as sns
#from .plot import Plot
from typing import Optional

class BarPlot():
    def __init__(self, data, x, y, hue, xlabel: str = "" , ylabel : str = "", title: str = "", library: Optional[str] = "seaborn", cache_data: Optional[bool] = False):
            
            if cache_data:
                self.data = data
            else:
                self.data = None
                
            self.plot = sns.barplot(data = data, x = x , y = y, hue = hue)
            
            self.ax = self.plot
            self.fig = self.ax.get_figure()
            
    def save(self, filename, extension):
        #print("Attempting to save")
        return self.fig.savefig(f"{filename}.{extension}")
        
            
            
            
            