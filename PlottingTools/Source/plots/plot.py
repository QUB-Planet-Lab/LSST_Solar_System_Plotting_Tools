from typing import Literal
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.offsetbox import AnchoredText


class Plot():
    '''A parent class which all plotting classes inherit from.'''
    def __init__(self, data, xlabel : str, ylabel : str = "", title: str = "", rc_params : dict = {}, plot_info : dict = {}):     
        self.data = data
        if rc_params:
            self.context = sns.set(rc=rc_params)# add all rc params here. Can be used for seaborn and matplotlib as long as it is figure level.
        else:
            self.context = None
        
        self.fig, self.ax = plt.subplots()
        
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.plot_info = plot_info

    def add_plot_info(self):
        if self.plot_info:
            text_box = ""
            
            for param in self.plot_info:
                text_box += f"{param}: {self.plot_info[param]}\n"
            text_box = text_box[0:-1]
            at = AnchoredText(
                text_box, prop=dict(size=15), frameon=True, loc='upper right')
            at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
            self.ax.add_artist(at)
            
        self.fig.suptitle(self.title)
        
        if self.xlabel:
            self.ax.set_xlabel(self.xlabel)
        if self.ylabel:
            self.ax.set_ylabel(self.ylabel)
        
    def save(self, file_name : str, extension : Literal['png', 'jpeg', 'pdf'] = 'png'):
        if self.context:
            self.context
        
        self.add_plot_info()
        
        plt.savefig(f"{file_name}.{extension}")
        
