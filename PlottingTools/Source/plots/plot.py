from typing import Literal
import matplotlib.pyplot as plt


class Plot():
    '''A parent class which all plotting classes inherit from.'''
    def __init__(self, data, xlabel : str, ylabel : str = "", title: str = ""):     
        self.data = data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
       
    def save(self, fig_name : str, extension : Literal['png', 'jpeg', 'pdf'] = 'png'):
        self.plot
        plt.title(self.title)
        if self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel:
            plt.ylabel(self.ylabel)
        plt.savefig(f"{fig_name}.{extension}")
        

