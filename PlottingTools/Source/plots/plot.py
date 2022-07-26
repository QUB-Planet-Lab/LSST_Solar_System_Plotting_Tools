from typing import Literal, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.offsetbox import AnchoredText

import pathlib
from plots.fonts import add_font

import matplotlib.font_manager

class Plot():
    '''A parent class which all plotting classes inherit from.'''
    
    def __init__(self, data, xlabel : str = "", ylabel : str = "",  title: str = "", library : Optional[str] = "seaborn", cache_data: Optional[bool] = False):     #rc_params : dict = {}
        
        if cache_data:
            self.data = data
        else:
            self.data = None
            
        self.library = library
        self.title = title
        
        '''
        if rc_params:
            self.context = sns.set(rc=rc_params)# add all rc params here. Can be used for seaborn and matplotlib as long as it is figure level.
        else:
            self.context = None
        '''    
        add_font()
        
    
        plt.style.use(f'{pathlib.Path(__file__).parent.absolute()}/styles/lsst.mplstyle')
        self.fig, self.ax = plt.subplots()
            
           
        self.title = title # Is is necessary to add these to variables?
        self.xlabel = xlabel
        self.ylabel = ylabel
        #self.plot_info = plot_info

        self.library = library

        
        self.fig.suptitle(self.title)
        self.fig.supxlabel(self.xlabel)
        self.fig.supylabel(self.ylabel)
      
        if self.xlabel:
            self.ax.set_xlabel('')
        if self.ylabel:
            self.ax.set_ylabel('')

    def update_title(self, _title):
        #self.title(_title)
        self.fig.suptitle(_title)
        return
    
    def update_xlabel(self, _xlabel):
        #self.xlabel(_xlabel)
        self.fig.supxlabel(_xlabel)
        return
    
    def update_ylabel(self, _ylabel):
        #self.ylabel(_ylabel)
        self.fig.supylabel(_ylabel)
        return
        
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
    
    def replot(**kwargs):
        for kwarg in kwargs:
            print(kwarg, kwargs[kwarg])
            ## add replot function, takes any of the columns from the dataframe and filters them to provide a new plot that maintains the old plot.
    
    def save(self, file_name : str, extension : Literal['png', 'jpeg', 'pdf'] = 'png'):
        #print(self.plot)
        
        self.fig.savefig(f"{file_name}.{extension}")
        
