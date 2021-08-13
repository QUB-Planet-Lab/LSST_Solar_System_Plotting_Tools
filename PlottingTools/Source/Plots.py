#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as ps
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math as mth
#from sbpy.data import Orbit as orbit
from astropy.time import Time
import re
import sys
import pytest
#Imports Package that contains the SQL interface
import DataAccessLayer as dal

sns.set_context(font_scale=1.4)
import warnings
warnings.filterwarnings(
    action='ignore', module='matplotlib.figure', category=UserWarning,
    message=('This figure includes Axes that are not compatible with tight_layout, '
             'so results might be incorrect.')
    
)

def run_plot_defaults(BirdsEye=False,HistogramPlot=False,HexbinPlot = False,date=float(int(Time.now().to_value('mjd'))),NightBefore=False,ShowPlot=False):
    NEODefaultFrame,ABeltDefaultFrame,MSSODefaultFrame,OSSODefaultFrame =None, None, None, None
    if NightBefore:
        date-=1
    
    if BirdsEye :
        
        NEODefaultFrame   = BirdsEyeViewPlotter(0,2,date,title = 'Near Earth Detections',filename='./NearEarthDetections-bev',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
        MSSODefaultFrame  = BirdsEyeViewPlotter(6,25,date,title = 'Mid Solar System Detections',filename='./MidSolarSystemDetections-bev',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        ABeltDefaultFrame = BirdsEyeViewPlotter(2,6,date,title = 'Asteroid Belt Detections',filename='./AsteroidBeltDetections-bev',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        OSSODefaultFrame  = BirdsEyeViewPlotter(25,100,date,title = 'Outer Solar System Detections',filename='./OuterSolarSystemDetections-bev',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
     
    if HistogramPlot:
        NEODefaultFrame   = HistogramPlot2D(0,2,date,title = 'Near Earth Detections, Filter:',filename='./NearEarthDetections-2DHist',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
        MSSODefaultFrame  = HistogramPlot2D(6,25,date,title = 'Mid Solar System Detections',filename='./MidSolarSystemDetections-2DHist',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        ABeltDefaultFrame = HistogramPlot2D(2,6,date,title = 'Asteroid Belt Detections',filename='./AsteroidBeltDetectiom-2DHist',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        OSSODefaultFrame  = HistogramPlot2D(25,100,date,title = 'Outer Solar System Detections',filename='./OuterSolarSystemDetections-2DHist',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
    
    if HexbinPlot :
        NEODefaultFrame   = HexPlot(0,2,date,title = 'Near Earth Detections, ',filename='./NearEarthDetections-hexbin',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
        MSSODefaultFrame  = HexPlot(6,25,date,title = 'Mid Solar System Detections',filename='./MidSolarSystemDetections-hexbin',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        ABeltDefaultFrame = HexPlot(2,6,date,title = 'Asteroid Belt Detections',filename='./AsteroidBeltDetections-hexbin',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        OSSODefaultFrame  = HexPlot(25,100,date,title = 'Outer Solar System Detections',filename='./OuterSolarSystemDetections-hexbin',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)        
         
from Barcharts import *
from Scatterplots import *
from Hist2D import *
from Hexbin import *
from BoxandBoxen import *
