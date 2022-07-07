from .plot import Plot
from seaborn import boxenplot
import matplotlib.pyplot as plt


from .styles.filter_color_scheme import COLOR_SCHEME

class BoxPlot(Plot):
    # does specific functionality need to be removed from here?
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None):
        super().__init__(data, xlabel, ylabel, title, rc_params)

        
        self.x = x
        self.y = y
        
        
        if not y:
            self.plot = self.ax.boxplot(x = data[self.x], labels=[''], vert=False, patch_artist = True)
            for median in self.plot['medians']:
                median.set_color('black')
                
                for patch in self.plot['boxes']:
                    patch.set(facecolor="#3CAE3F") # add color optionality
                
        elif not x:
            self.plot = self.ax.boxplot(x = data[self.y], vert=True, patch_artist=True, labels=[''])
            for median in self.plot['medians']:
                median.set_color('black')
            for patch in self.plot['boxes']:
                patch.set(facecolor="#3CAE3F")
                
        else:
            # add optionality to have the boxes vertically aligned?
            filter_x = []
            cols = data[self.y].unique()
            for col in cols:
                filter_x.append(data[data[self.y] == col][self.x])
            
            self.plot = self.ax.boxplot(x = filter_x, labels = cols,  vert=False, patch_artist=True)
            for i, patch in enumerate(self.plot['boxes']):
                patch.set(facecolor = COLOR_SCHEME[cols[i]])
                
            for median in self.plot['medians']:
                median.set_color('black')
    
class BoxenPlot(Plot):
    def __init__(self, data, x = None, y = None, xlabel: str = "" , ylabel : str = "", title: str = "", rc_params : dict = {}, ax = None):
        super().__init__(data, xlabel, ylabel, title, rc_params)
        
        self.x = x
        self.y = y
       
        if not y:
            self.plot = boxenplot(x = data[self.x], ax = self.ax).set(xlabel="", ylabel="")
        elif not x:
            self.plot = boxenplot(y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")
        else:
            self.plot = boxenplot(x = data[self.x], y = data[self.y], ax = self.ax).set(xlabel="", ylabel="")

        
        
 