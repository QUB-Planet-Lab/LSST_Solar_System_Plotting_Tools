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
from astropy.time import TimeMJD
from astropy import units
import multiprocessing as mp
import threading
import re
import sys
import pytest
#Imports Package that contains the SQL interface
from DAL import DataAccessLayer as dal
from Functions import *

sns.set_context(font_scale=1.4)
import warnings
warnings.filterwarnings(
    action='ignore', module='matplotlib.figure', category=UserWarning,
    message=('This figure includes Axes that are not compatible with tight_layout, '
             'so results might be incorrect.')
    
)

def Heliocentric_BirdsEyeView(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,PlotPlanetsOnPlot,Filters]
    
    return BirdsEyeViewPlotter(*variables,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1)
    
def Topocentric_BirdsEyeView(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,PlotPlanetsOnPlot,Filters]
    
    return BirdsEyeViewPlotter(*variables,xyscale=['topocentricx','topocentricy','topocentric'],QueryNum=4)    

    
def Heliocentric_HistogramPlot2D(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,PlotPlanetsOnPlot,Filters]
    
    return HistogramPlot2D(*variables,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1)
    
def Topocentric_HistogramPlot2D(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,PlotPlanetsOnPlot,Filters]
    
    return HistogramPlot2D(*variables,xyscale=['topocentricx','topocentricy','topocentric'],QueryNum=4)    

def Heliocentric_HexPlot(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,GridSize=40,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,GridSize,PlotPlanetsOnPlot,Filters]
    
    return HexPlot(*variables,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1)
    
def Topocentric_HexPlot(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,GridSize=40,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,GridSize,PlotPlanetsOnPlot,Filters]
    
    return HexPlot(*variables,xyscale=['topocentricx','topocentricy','topocentric'],QueryNum=4)    


#Heliocentric_BirdsEyeView(0,2,'60042',title = 'Near Earth Detections',KeepData=False,ShowPlot=True)
#Heliocentric_HistogramPlot2D(0,2,'60042',title = 'Near Earth Detections',KeepData=False,ShowPlot=True)
#Heliocentric_HexPlot(0,2,'60042',title = 'Near Earth Detections',KeepData=False,ShowPlot=True)


#Topocentric_BirdsEyeView(0,2,'60042',title = 'Near Earth Detections',KeepData=False,ShowPlot=True)
#Topocentric_HistogramPlot2D(0,2,'60042',title = 'Near Earth Detections',KeepData=False,ShowPlot=True)    
#Topocentric_HexPlot(0,2,'60042',title = 'Near Earth Detections',KeepData=False,ShowPlot=True)  


# In[ ]:



# boxwhisker_plot(0,2,date=60042,day=None,month=None,year=None,boxOrBoxen=2,
#                        title='NaN',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
#                        DataFrame=None,Filters=None)


# In[ ]:


#Weekly24hrHist(0,2,60042,ShowPlot=True)
#Weekly24hrHist(25,100,60042,DateInterval=49,ShowPlot=True)


# In[ ]:



# MonthlyHelioDistHist(date=60042,day=None,month=None,year=None,title='NaN', filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True, )


# In[ ]:


#Months = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#Dates = [Months[int(date.split('-')[1])-1] + ', '+date.split('-')[0] for date in Dates]


# In[ ]:


##%%time

# YearlyHelioDistHist(date=60042,day=None,month=None,year=None,title='NaN',filename=None,DateInterval = 9 ,KeepData=False,ShowPlot=True,
#                   DistanceMinMax=[[6,25],[1.00,1.01]]
#                    )


# In[ ]:


# %%time 
#     YearlyHelioDistHist(date=60042,day=None,month=None,year=None,title='NaN',filename=None,DateInterval = 4 ,KeepData=False,ShowPlot=True,
#                     # DistanceMinMax=[[round(num,2),round(np.linspace(1.05,2,20)[i],2)]for i,num in enumerate(np.linspace(1,1.95,20))]
#                        )


# In[ ]:



#0.5 to 1.5 au and 1.5 to 3 au, and 1 to 1.6 au for example
#HelioDistHist(60042,DateInterval = 3,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3]])
#HelioDistHist(60042,DateInterval = 1)
#HelioDistHist(60042,DateInterval = 2)
#HelioDistHist(60042,DateInterval = 3)
#HelioDistHist(60042,DateInterval = 4)
#HelioDistHist(60042,DateInterval = 5)
#HelioDistHist(60042,DateInterval = 8)
#HelioDistHist(60042,DateInterval = 7)
#HelioDistHist(60042,DateInterval = 21)
#HelioDistHist(60042,DateInterval = 49)


# In[ ]:


#HelioDistHist(60042,DateInterval = 7,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3],[3,3.5],[3.5,4]])
#HelioDistHist(60042,DateInterval = 3,DistanceMinMax=listthing)


# In[ ]:


#violin_plot(0,2,60042,title = 'Near Earth Detections')


# In[ ]:



#max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
#theframe = iqeaHistogramPlot2D(a_min=27,a_max=80,KeepData=True)
# iqeaHistogramPlot2D(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',])
# iqeaHistogramPlot2D(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','e','eccentricity-semimajoraxis'],xylabels=['semimajor axis (au)','eccentricity',])
# iqeaHistogramPlot2D(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','incl','inclination-semimajoraxis'],xylabels=['semimajor axis (au)','inclination (degrees)'])


# theframe = iqeaHexPlot(a_min=27,a_max=80,KeepData=True,xyscale=['a','incl','inclination-semimajoraxis'],xylabels=['semimajor axis (au)','inclination (degrees)'])
# iqeaHexPlot(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',])
# iqeaHexPlot(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','e','eccentricity-semimajoraixs'],xylabels=['semimajor axis (au)','eccentricity'])
# iqeaHexPlot(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','incl','inclination-semimajoraxis'],xylabels=['semimajor axis (au)','inclination (degrees)'])


# In[ ]:





# In[ ]:


# startdate=None, enddate=None, a_min=None, a_max=None, q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None
def iqea_scatter_plot(date=None,day=None,month=None,year=None,title='',filename=None,DateInterval =1,KeepData=False,
                      ShowPlot=True,DataFrame=None,plots = 'iqea',startdate=None, enddate=None, a_min=None, a_max=None,
                      q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None):
    arguments = [date,day,month,year,title,filename,DateInterval,KeepData, ShowPlot]
    usefulplots = [['q','a'],['a'],['q','a']]
    labels = {'i': 'inclination (degrees)','q': 'perihelion (au)','e' :'eccentricity','a': 'semimajor axis (au)'}
    QueryNum=7
    if (startdate is None and enddate is None): QueryNum = 8
    if DataFrame is None:
        DataFrame = Queries(startdate,enddate,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaBirdsEyeView(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
        if yaxis == 'q': 
            for xaxis in usefulplots[1]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaBirdsEyeView(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaBirdsEyeView(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
    if KeepData : return DataFrame
         

def iqea_hexbin_plot(date=None,day=None,month=None,year=None,title='NaN',filename=None,DateInterval =1,KeepData=False,
                      ShowPlot=True,DataFrame=None,plots = 'iqea',startdate=None, enddate=None, a_min=None, a_max=None,
                      q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None):
    
    arguments = [date,day,month,year,title,filename,DateInterval,KeepData, ShowPlot]
    usefulplots = [['q','a'],['a'],['q','a']]
    labels = {'i': 'inclination (degrees)','q': 'perihelion (au)','e' :'eccentricity','a': 'semimajor axis (au)'}
    QueryNum=7
    if (startdate is None and enddate is None): QueryNum = 8
    if DataFrame is None:
        DataFrame = Queries(startdate,enddate,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHexPlot(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'q': 
            for xaxis in usefulplots[1]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHexPlot(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
                
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHexPlot(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
                
    if KeepData: return DataFrame
         


    



def iqea_hist_2d_plot(date=None,day=None,month=None,year=None,title='',filename=None,DateInterval =1,KeepData=False,
                      ShowPlot=True,DataFrame=None,plots = 'iqea',startdate=None, enddate=None, a_min=None, a_max=None,
                      q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None):
   
    arguments = [date,day,month,year,title,filename,DateInterval,KeepData, ShowPlot]
    usefulplots = [['q','a'],['a'],['q','a']]
    labels = {'i': 'inclination (degrees)','q': 'perihelion (au)','e' :'eccentricity','a': 'semimajor axis (au)'}
    QueryNum=7
    if (startdate is None and enddate is None): 
        QueryNum = 8
    if DataFrame is None:
        DataFrame = Queries(startdate,enddate,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
        if yaxis == 'q':
            for xaxis in usefulplots[1]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
    if KeepData: return DataFrame
                

# iqea_scatter_plot(title='',a_min=3.04,a_max=3.05,e_min=0,e_max=1,filename='inner_solar_system_scat')
# iqea_hist_2d_plot(title='',a_min=3.04,a_max=3.05,e_min=0,e_max=1,filename='inner_solar_system_2d_hist')
# iqea_hexbin_plot(title='',a_min=3.04,a_max=3.05,e_min=0,e_max=1,filename='inner_solar_system_2d_hex')

# iqea_scatter_plot(DataFrame=theframe,a_min=0,a_max=6,e_min=0,e_max=0.99999,ShowPlot=False)    
#theframe = iqea_hist_2d_plot(a_min=0,a_max=6,e_min=0,e_max=0.99999)
# iqea_hexbin_plot(DataFrame=theframe.sample(5000),a_min=0,a_max=6,e_min=0,e_max=0.99999,ShowPlot=False)
#iqea_hist_2d_plot(a_min=0,a_max=6,e_min=0,e_max=1,ShowPlot=False, filename='inner_solar_system_2d_hist.pdf')


# In[ ]:


#Queries(None,None,None,None,8,3.04,3.05,None,None,None,None , 0, 1)


# In[ ]:


def run_plot_defaults(BirdsEye=False,HistogramPlot=False,HexbinPlot = False,date=float(int(Time.now().to_value('mjd'))),NightBefore=False,ShowPlot=False):
    NEODefaultFrame,ABeltDefaultFrame,MSSODefaultFrame,OSSODefaultFrame =None, None, None, None
    if NightBefore:
        date-=1
    
    if BirdsEye :
        
        NEODefaultFrame   = BirdsEyeViewPlotter(0,2,date,title = 'Near Earth Detections',filename='./Defaults/NearEarthDetections-bev',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
        MSSODefaultFrame  = BirdsEyeViewPlotter(6,25,date,title = 'Mid Solar System Detections',filename='./Defaults/MidSolarSystemDetections-bev',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        ABeltDefaultFrame = BirdsEyeViewPlotter(2,6,date,title = 'Asteroid Belt Detections',filename='./Defaults/AsteroidBeltDetections-bev',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        OSSODefaultFrame  = BirdsEyeViewPlotter(25,100,date,title = 'Outer Solar System Detections',filename='./Defaults/OuterSolarSystemDetections-bev',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
     
    if HistogramPlot:
        NEODefaultFrame   = HistogramPlot2D(0,2,date,title = 'Near Earth Detections, Filter:',filename='./Defaults/NearEarthDetections-2DHist',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot,Filters='grizy') 
        #MSSODefaultFrame  = HistogramPlot2D(6,25,date,title = 'Mid Solar System Detections',filename='./Defaults/MidSolarSystemDetections-2DHist',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        #ABeltDefaultFrame = HistogramPlot2D(2,6,date,title = 'Asteroid Belt Detections',filename='./Defaults/AsteroidBeltDetectiom-2DHist',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        #OSSODefaultFrame  = HistogramPlot2D(25,100,date,title = 'Outer Solar System Detections',filename='./Defaults/OuterSolarSystemDetections-2DHist',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
    
    if HexbinPlot :
        NEODefaultFrame   = HexPlot(0,2,date,title = 'Near Earth Detections, ',filename='./Defaults/NearEarthDetections-hexbin',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot,Filters='grizy') 
        #MSSODefaultFrame  = HexPlot(6,25,date,title = 'Mid Solar System Detections',filename='./Defaults/MidSolarSystemDetections-hexbin',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        #ABeltDefaultFrame = HexPlot(2,6,date,title = 'Asteroid Belt Detections',filename='./Defaults/AsteroidBeltDetections-hexbin',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
        #OSSODefaultFrame  = HexPlot(25,100,date,title = 'Outer Solar System Detections',filename='./Defaults/OuterSolarSystemDetections-hexbin',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)        
              
#run_plot_defaults(False,True,True,date = 60042,NightBefore=False,ShowPlot=True)

