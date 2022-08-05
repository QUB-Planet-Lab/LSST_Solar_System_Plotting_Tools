from typing import Literal, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.offsetbox import AnchoredText


import pandas as pd

import pathlib
from plots.fonts import add_font

import matplotlib.font_manager

class Plot():
    '''A parent class which all plotting classes inherit from.'''
    
    def __init__(self, data, xlabel : str = "", ylabel : str = "",  title: str = "", library : Optional[str] = "seaborn", cache_data: Optional[bool] = False, data_copy : Optional[pd.DataFrame] = None):     #rc_params : dict = {}
        
        if cache_data:
            if data_copy is not None:
                self.data = data_copy
            else:
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
        #add_font()
        
    
        #plt.style.use(f'{pathlib.Path(__file__).parent.absolute()}/styles/lsst.mplstyle')
        # add dimensions to figure
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
    
    def save(self, file_name : str, extension : Literal['png', 'jpeg', 'pdf'] = 'png'):
        #print(self.plot)
        
        self.fig.savefig(f"{file_name}.{extension}")
        
class MultiPlot(Plot):
    def __init__(self, title: str = "", dimensions : Optional[list] = [1,1], plots : Optional[list] = None):

       
        self.title = title
        
        self.show = False
        
        self.fig = plt.figure(constrained_layout=True)

        self.gs = self.fig.add_gridspec(
            nrows = dimensions[0],
            ncols = dimensions[1]
        )
        
        plt.close()
            
    @staticmethod
    def parse_position(position):
        idx = position.split(':')
        if len(idx) == 2:
            start = int(idx[0])
            end = int(idx[1])
            
            return {'start' : start, 'end': end + 1}
        elif len(idx) == 1:
            spot = int(idx[0])
            return {'start' : spot, 'end' : spot + 1}
        else:
            raise Exception("Input error") # add reasoning
            
    def add(self, plots: list):

        for i, plot in enumerate(plots):
            col = self.parse_position(plot.position[0])
           
            row = self.parse_position(plot.position[1])
            
            ax = self.fig.add_subplot(self.gs[
                    row['start'] : row['end'],
                    col['start'] : col['end']
                    ])
            
            plot.create_plot(ax = ax)
            
            plt.close()
        
        return self.fig
           
        
      
        