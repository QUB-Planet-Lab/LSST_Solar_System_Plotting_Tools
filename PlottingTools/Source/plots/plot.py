from typing import Literal
import matplotlib.pyplot as plt
import seaborn as sns

class Plot():
    '''A parent class which all plotting classes inherit from.'''
    def __init__(self, data, xlabel : str, ylabel : str = "", title: str = "", rc_params : dict = {}):     
        self.data = data
        if rc_params:
            self.context = sns.set(rc=rc_params)# add all rc params here. Can be used for seaborn and matplotlib as long as it is figure level.
        else:
            self.context = None
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        
    def add_plot_info(self):
        plt.title(self.title)
        if self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel:
            plt.ylabel(self.ylabel)
        # add legend here also
        
    
    def save(self, file_name : str, extension : Literal['png', 'jpeg', 'pdf'] = 'png'):
        # Need to validate these arguments, filepath?
        if self.context:
            self.context
        self.plot
        self.add_plot_info()
        plt.savefig(f"{file_name}.{extension}")
        

