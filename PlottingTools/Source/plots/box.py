from .plot import Plot
from seaborn import boxplot, boxenplot

class BoxPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        print(x, y)
        self.x = x
        self.y = y
        if ax:
            self.plot = boxplot(x = data[self.x], y = data[self.y], ax = ax)
        else:
            if not y:
                self.plot = boxplot(x = data[self.x])
            elif not x:
                self.plot = boxplot(y = data[self.y])
            else:
                self.plot = boxplot(x = data[self.x], y = data[self.y])
            
    
class BoxenPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        self.x = x
        self.y = y
        
        if ax:
            self.plot = boxenplot(x = data[self.x], y = data[self.y], ax = ax)
        
        else:
            if not y:
                self.plot = boxenplot(x = data[self.x])
            elif not x:
                self.plot = boxenplot(y = data[self.y])
            else:
                self.plot = boxenplot(x = data[self.x], y = data[self.y])
            
        
        
 