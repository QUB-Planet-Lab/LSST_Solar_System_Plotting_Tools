#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as ps
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math as mth
#from sbpy.data import Orbit as orbit
from astropy.time import Time
from astropy import units
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


# In[2]:


# def check_next(pair):
#     if (any(i is not None for i in pair)):
#         return """\n\tAND\n"""
#     return ''


# def Queries(startdate=None, enddate=None, mindistance=None, maxdistance=None, Query=None, a_min=None, a_max=None,
#             q_min=None, q_max=None, i_min=None,
#             i_max=None, e_min=None, e_max=None):
#     min_max_pair = [[q_min, q_max], [i_min, i_max], [e_min, e_max], [a_min, a_max], [startdate, enddate]]
#     params = {"startdate": startdate, "enddate": enddate, "mindistance": mindistance,
#               "maxdistance": maxdistance, 'a_min': a_min, 'a_max': a_max, 'q_min': q_min, 'q_max': q_max
#         , 'i_min': i_min,
#               'i_max': i_max, 'e_min': e_min, 'e_max': e_max}
#     if Query == 1:
#         cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.midpointtai, diasources.mag,
#                diasources.filter, sssources.heliocentricx,sssources.heliocentricy 
#                FROM diasources,sssources WHERE 
#                (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) 
#                AND 
#                (sssources.heliocentricdist > %(mindistance)s AND sssources.heliocentricdist < %(maxdistance)s) 
#                AND 
#                (diasources.diasourceid=sssources.diasourceid)"""
#     elif Query == 2:
#         cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.mag,
#                diasources.filter, sssources.heliocentricdist, sssources.topocentricdist,
#                sssources.eclipticbeta FROM
#                diasources,sssources
#                WHERE
#                (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) AND
#                (sssources.heliocentricdist > %(mindistance)s AND sssources.heliocentricdist < %(maxdistance)s) AND
#                (diasources.diasourceid=sssources.diasourceid)
#                """
#     elif Query == 3:
#         cmd = """SELECT COUNT(DISTINCT diasources.ssobjectid)
#                FROM
#                diasources,sssources
#                WHERE
#                midpointtai BETWEEN %(startdate)s AND %(enddate)s
#                AND
#                sssources.heliocentricdist BETWEEN %(mindistance)s AND %(maxdistance)s
#                AND
#                (diasources.diasourceid=sssources.diasourceid)
#             """

#     elif Query == 4:
#         cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.midpointtai, diasources.mag,
#                diasources.filter, sssources.topocentricx,sssources.topocentricy 
#                FROM diasources,sssources WHERE (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) 
#                AND 
#                (sssources.topocentricdist > %(mindistance)s AND sssources.topocentricdist < %(maxdistance)s) 
#                AND 
#                (diasources.diasourceid=sssources.diasourceid)"""
#     elif Query == 5:
#         cmd = """SELECT mpcdesignation, ssobjectid, q,e,incl,mpch
#                FROM MPCORB 
#                WHERE
#                (e <1) 
#                AND 
#                (q/(1-e) BETWEEN %(a_min)s AND %(a_max)s)"""
#         df = dal.create_connection_and_queryDB(cmd, params)
#         df['a'] = df["q"] / (1 - df["e"])
#         print(cmd)
#         return df
#     elif Query == 6:
#         cmd="""select Query.mpcdesignation, Query.ssobjectid, diaSources.diaSourceid, Query.q,Query.e,Query.incl,Query.mpch, diaSources.midPointTai,a
#             from  (
#         select MPCORB.mpcdesignation, MPCORB.ssobjectid, q,e,incl,mpch,q/(1-e) as a
#             from MPCORB where 
#             (e < 1)
#          AND (q/(1-e) BETWEEN %(a_min)s AND %(a_max)s) 
#         ) as Query
        
#         JOIN diaSources USING (ssobjectid)
#         JOIN ssSources USING (diaSourceid)
#         WHERE (diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s)
#         """
#         df = dal.create_connection_and_queryDB(cmd, params)
#         #df['a'] = df["q"] / (1 - df["e"])
#         print(cmd)
#         return df
#     elif Query == 7:
#         # max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
#         count=0
#         cmd = """SELECT MPCORB.mpcdesignation, MPCORB.ssobjectid, diaSources.diaSourceid, q,e,incl,mpch, diaSources.midPointTai
#         FROM MPCORB 
#         JOIN diaSources USING (ssobjectid)
#         JOIN ssSources USING (diaSourceid)
#         """
#         if (any(i is not None for i in [a_min, a_max, q_min, q_max, i_min, i_max, e_min, e_max])):
#             cmd += """\nWHERE\n"""
#         count+=1
#         if (q_min is not None and q_max is not None):
#             cmd += """\t(q BETWEEN %(q_min)s AND %(q_max)s)"""
#             check=cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (q_min is not None and q_max is None):
#             cmd += """\t(q > %(q_min)s )"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (q_min is None and q_max is not None):
#             cmd += """\t(q < %(q_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         count+=1
#         if (i_min is not None and i_max is not None):
#             cmd += """\t(incl BETWEEN %(i_min)s AND %(i_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (i_min is not None and i_max is None):
#             cmd += """\t(incl > %(i_min)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (i_min is None and i_max is not None):
#             cmd += """\t(incl < %(i_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         count+=1
#         if (e_min is not None and e_max is not None):
#             cmd += """\t(e BETWEEN %(e_min)s AND %(e_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (e_min is not None and e_max is None):
#             cmd += """\t(e > %(e_min)s )"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (e_min is None and e_max is not None):
#             cmd += """\t(e < %(e_max)s )"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         if (e_min is not None and e_min >= 1): a_min, a_max = None, None
#         count+=1
#         if (a_min is not None and a_max is not None):
#             cmd += """\t(q/(1-e) BETWEEN %(a_min)s AND %(a_max)s) """
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (a_min is not None and a_max is None):
#             cmd += """\t(q/(1-e) > %(a_min)s) """
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (a_min is None and a_max is not None):
#             cmd += """\t(q/(1-e) < %(a_max)s) """
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         count+=1
#         #         if ( tp_min  is not None and tp_max is not None):
#         #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#         #         elif tp_min  is not None and tp_max is None):
#         #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#         #         elif (tp_min  is None and tp_max is not None):
#         #             """\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#         if (startdate is not None and enddate is not None):
#             cmd += """\tdiaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 print(pair,check!=cmd)
#                 if check != cmd:
#                     break
#         elif (startdate is not None and enddate is None):
#             cmd += """\tdiaSources.midPointTai > %(startdate)s"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (startdate is None and enddate is not None):
#             cmd += """\tdiaSources.midPointTai < %(enddate)s"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         df = dal.create_connection_and_queryDB(cmd, params)
#         if e_max is not None and e_max < 1:
#             df['a'] = df['q'] / (1 - df['e'])
#         return df
#     elif Query == 8:
#         min_max_pair = [[q_min, q_max], [i_min, i_max], [e_min, e_max], [a_min, a_max]]
#         # max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
#         count=0
#         cmd = """SELECT MPCORB.mpcdesignation, MPCORB.ssobjectid, q,e,incl,mpch
#         FROM MPCORB 
#         """
#         if (any(i is not None for i in [a_min, a_max, q_min, q_max, i_min, i_max, e_min, e_max])):
#             cmd += """\nWHERE\n"""
#         count+=1
#         if (q_min is not None and q_max is not None):
#             cmd += """\t(q BETWEEN %(q_min)s AND %(q_max)s)"""
#             check=cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (q_min is not None and q_max is None):
#             cmd += """\t(q > %(q_min)s )"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (q_min is None and q_max is not None):
#             cmd += """\t(q < %(q_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         count+=1
#         if (i_min is not None and i_max is not None):
#             cmd += """\t(incl BETWEEN %(i_min)s AND %(i_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (i_min is not None and i_max is None):
#             cmd += """\t(incl > %(i_min)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (i_min is None and i_max is not None):
#             cmd += """\t(incl < %(i_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         count+=1
#         if (e_min is not None and e_max is not None):
#             cmd += """\t(e BETWEEN %(e_min)s AND %(e_max)s)"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (e_min is not None and e_max is None):
#             cmd += """\t(e > %(e_min)s )"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (e_min is None and e_max is not None):
#             cmd += """\t(e < %(e_max)s )"""
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         if (e_min is not None and e_min >= 1): a_min, a_max = None, None
#         count+=1
#         if (a_min is not None and a_max is not None):
#             cmd += """\t(q/(1-e) BETWEEN %(a_min)s AND %(a_max)s) """
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (a_min is not None and a_max is None):
#             cmd += """\t(q/(1-e) > %(a_min)s) """
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         elif (a_min is None and a_max is not None):
#             cmd += """\t(q/(1-e) < %(a_max)s) """
#             check = cmd
#             for pair in min_max_pair[count:]:
#                 cmd += check_next(pair)
#                 if check != cmd:
#                     break
#         count+=1
#         #         if ( tp_min  is not None and tp_max is not None):
#         #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#         #         elif tp_min  is not None and tp_max is None):
#         #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#         #         elif (tp_min  is None and tp_max is not None):
#         #             """\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
#         df = dal.create_connection_and_queryDB(cmd, params)
#         if e_max is not None and e_max < 1:
#             df['a'] = df['q'] / (1 - df['e'])
#         return df
#     else:
#         print('No Query Called')
#         return

#     df = dal.create_connection_and_queryDB(cmd, params)

#     return df


# In[3]:


#print(Queries(None,None,mindistance =None,maxdistance=None,Query=7,a_min=None,a_max=None,q_min=27,q_max=80,i_min=None,i_max=None , e_min =None, e_max=0.99999))
#print(Queries(None,None,mindistance =None,maxdistance=None,Query=7,a_min=None,a_max=None,q_min=None,q_max=1,i_min=2,i_max=None , e_min =7, e_max=None))


# In[4]:


#Queries(60042.75,60043.75,mindistance =None,maxdistance=None,Query=7,a_min=27,a_max=80,q_min=None,q_max=None,i_min=None,i_max=None , e_min =None, e_max=None)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[5]:


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


# In[6]:



#boxwhisker_plot(0,6,date=60042,day=None,month=None,year=None,boxOrBoxen=2,
#                        title='NaN',filename=None,DateInterval =7,KeepData=False,ShowPlot=True,
#                        DataFrame=None,Filters=None)


# In[ ]:





# In[7]:



    
    
    
#Weekly24hrHist(0,2,60042,ShowPlot=True)
#Weekly24hrHist(25,100,60042,DateInterval=49,ShowPlot=True)


# In[8]:


# def FastHelioDistHist(date=None,day=None,month=None,year=None,title='NaN', 
#                   filename=None,DateInterval = 7 ,KeepData=False,ShowPlot=True,
#                   DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
    
   
    
#     startdate, enddate, title = VariableTesting(0,0,date,day,month,year,title,DateInterval)
#     dates = np.linspace(0,DateInterval-1,DateInterval)
#     counters = np.ndarray((len(dates)*len(DistanceMinMax),3))
#     ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1)-0.5)
       
#     count=0
    
#     distances = [] 
#     for i,offset in enumerate(dates):   
#         for MinMax in DistanceMinMax:
#             distances+=[[startdate+offset, startdate+offset+1, *MinMax,3]]
    
#     with mp.Pool(4*mp.cpu_count()) as pool:
#         result_list = pool.starmap(Queries, distances)
#         pool.start()
#         pool.join()

#     return result_list
        
        
#         #for j in range(len(distances)):
#             #df = Queries(*distances[j])
#         #    counters[count,:] = [offset+startdate,df['count'].values[0],j]
#         #    count += 1
    
#     NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
#     legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
#     fig = plt.subplots(figsize=(3*DateInterval,4))
    
    
    
#     ax = sns.barplot(x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'])
#     ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
    
    
#     xval = -0.5
#     numberofdistances=0
#     xvalcount = 0
#     for i,patch in enumerate(ax.patches):
        
#         patch.set_width(1/len(distances))
#         patch.set_x(xval+numberofdistances)
#         xval+=1
#         plt.axvline(xval,color='black')
#         xvalcount+=1
#         if xvalcount==DateInterval:
#             xvalcount=0
#             xval=-0.5
#             numberofdistances+=1/len(distances)
        
    
#     ax.set_xticks(ticks)
#     ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in dates+startdate]
#     ax.set_xticklabels(ProperDateLabels+[DateorMJD(MJD=enddate,ConvertToIso=False).to_value(format='iso',subfmt='date')],horizontalalignment='left',rotation=-40)
#     ax.set(yscale="log")
#     if (filename is not None):
#         SavePlot(filename, dict(),ShowPlot)
#     else:
#         SavePlot(title+'-fastheliodisthist' ,dict(),ShowPlot)
#     if (KeepData == True):
#         return df
# #0.5 to 1.5 au and 1.5 to 3 au, and 1 to 1.6 au for example
# #FastHelioDistHist(60042,DateInterval = 3,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3]])


# In[9]:



# date = DateorMJD(MJD=60042,ConvertToIso=False).to_value(format='iso',subfmt='date').split('-')
# date[-1] = '01'

# DateInterval = 8
# DistanceMinMax=[[0,2],
#                 [2,6],[6,25],
#                 [25,100]]
# counters = np.ndarray((DateInterval*len(DistanceMinMax),3))

# ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1)-0.5)
# count=0
# Dates = []
# for i in range(0,DateInterval):
    
#     startdate =Time('-'.join(date)).to_value('mjd')
#     Dates+=[DateorMJD(MJD=startdate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
#     if int(date[1]) ==12:
#         date[0] = str(int(date[0])+1); 
#         date[1] = '01'
#     else:
#         date[1] = str(int(date[1])+1)
#         if int(date[1]) <10:
#             date[1] = '0'+date[1]
#     enddate =Time('-'.join(date)).to_value('mjd')
#     print(startdate,enddate)
#     distances = []
#     for MinMax in DistanceMinMax:
#         distances+=[[startdate+0.75, enddate+0.75, *MinMax,3]]
        
#     for j in range(len(distances)):
#         df = Queries(*distances[j])
#         counters[count,:] = [startdate,df['count'].values[0],j]
#         count += 1
# #Dates+=[DateorMJD(MJD=enddate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
# Dates = [ '-'.join(date.split('-')[0:2]) for date in Dates]
# NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
# ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1)-0.5)
# legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
# fig = plt.subplots(figsize=(3*DateInterval,4))
# ax =sns.barplot(x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'])
# ax.set_xticks(ticks)
# ax.set_xticklabels(Dates,horizontalalignment='left',rotation=-40)
# ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
# ax.set(yscale="log")
# xval = -0.5
# numberofdistances=0
# xvalcount = 0
# for i,patch in enumerate(ax.patches):

#     patch.set_width(1/len(distances))
#     patch.set_x(xval+numberofdistances)
#     xval+=1
#     plt.axvline(xval,color='black')
#     xvalcount+=1
#     if xvalcount==DateInterval:
#         xvalcount=0
#         xval=-0.5
#         numberofdistances+=1/len(distances)


# In[ ]:





# In[10]:



# MonthlyHelioDistHist(date=60042,day=None,month=None,year=None,title='NaN', filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True, )


# In[11]:


#Months = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#Dates = [Months[int(date.split('-')[1])-1] + ', '+date.split('-')[0] for date in Dates]


# In[12]:


##%%time

# YearlyHelioDistHist(date=60042,day=None,month=None,year=None,title='NaN',filename=None,DateInterval = 9 ,KeepData=False,ShowPlot=True,
#                   DistanceMinMax=[[6,25],[1.00,1.01]]
#                    )


# In[13]:


# %%time 
#     YearlyHelioDistHist(date=60042,day=None,month=None,year=None,title='NaN',filename=None,DateInterval = 4 ,KeepData=False,ShowPlot=True,
#                     # DistanceMinMax=[[round(num,2),round(np.linspace(1.05,2,20)[i],2)]for i,num in enumerate(np.linspace(1,1.95,20))]
#                        )


# In[14]:





# In[15]:



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


# In[16]:


#HelioDistHist(60042,DateInterval = 7,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3],[3,3.5],[3.5,4]])
#HelioDistHist(60042,DateInterval = 3,DistanceMinMax=listthing)


# In[17]:



#violin_plot(0,2,60042,title = 'Near Earth Detections')
#violin_plot(25,50,60042,title = 'Outer Solar System Detections')


# In[18]:



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
        DataFrame = Queries(None,None,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                iqeaBirdsEyeView(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'q': 
            for xaxis in usefulplots[1]:
                iqeaBirdsEyeView(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                iqeaBirdsEyeView(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
    if DateInterval: return DataFrame
         

def iqea_hexbin_plot(date=None,day=None,month=None,year=None,title='NaN',filename=None,DateInterval =1,KeepData=False,
                      ShowPlot=True,DataFrame=None,plots = 'iqea',startdate=None, enddate=None, a_min=None, a_max=None,
                      q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None):

    arguments = [date,day,month,year,title,filename,DateInterval,KeepData, ShowPlot]
    usefulplots = [['q','a'],['a'],['q','a']]
    labels = {'i': 'inclination (degrees)','q': 'perihelion (au)','e' :'eccentricity','a': 'semimajor axis (au)'}
    QueryNum=7
    if (startdate is None and enddate is None): QueryNum = 8
    if DataFrame is None:
        DataFrame = Queries(None,None,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                iqeaHexPlot(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'q': 
            for xaxis in usefulplots[1]:
                iqeaHexPlot(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                iqeaHexPlot(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
    if DateInterval: return DataFrame
         


    



def iqea_hist_2d_plot(date=None,day=None,month=None,year=None,title='',filename=None,DateInterval =1,KeepData=False,
                      ShowPlot=True,DataFrame=None,plots = 'iqea',startdate=None, enddate=None, a_min=None, a_max=None,
                      q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None):
    arguments = [date,day,month,year,title,filename,DateInterval,KeepData, ShowPlot]
    usefulplots = [['q','a'],['a'],['q','a']]
    labels = {'i': 'inclination (degrees)','q': 'perihelion (au)','e' :'eccentricity','a': 'semimajor axis (au)'}
    QueryNum=7
    if (startdate is None and enddate is None): QueryNum = 8
    if DataFrame is None:
        DataFrame = Queries(None,None,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'q': 
            for xaxis in usefulplots[1]:
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #print(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                #rint(xaxis,yaxis,labels[xaxis],labels[yaxis],labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0])
    if DateInterval: return DataFrame
                

#iqea_scatter_plot(DataFrame=theframe,a_min=0,a_max=6,e_min=0,e_max=0.99999)    
#iqea_hist_2d_plot(DataFrame=theframe,a_min=0,a_max=6,e_min=0,e_max=0.99999,)
#iqea_hexbin_plot(title='',DataFrame=theframe,a_min=0,a_max=6,e_min=0,e_max=0.99999,)

# iqea_scatter_plot(DataFrame=theframe.sample(5000),a_min=0,a_max=6,e_min=0,e_max=0.99999,ShowPlot=False)    
# iqea_hist_2d_plot(DataFrame=theframe.sample(5000),a_min=0,a_max=6,e_min=0,e_max=0.99999,ShowPlot=False)
# iqea_hexbin_plot(DataFrame=theframe.sample(5000),a_min=0,a_max=6,e_min=0,e_max=0.99999,ShowPlot=False)


# In[ ]:





# In[ ]:





# In[ ]:


## RunPlotDefaults: Used for daily running to generate default plots.
## BirdsEye : Boolean on whether to run default birdseyeview plots
## HistogramPlot : Boolean on whether to run default 2D Histplot plots
## HexbinPlot : Boolean on whether to run default Hexbin plots
## date : date on which to run defaults (mjd)
## NightBefore : Changes default behaviour from the next night based on user entered date to the night
##               before for daily run defaults, 
# def run_plot_defaults(BirdsEye=False,HistogramPlot=False,HexbinPlot = False,date=float(int(Time.now().to_value('mjd'))),NightBefore=False,ShowPlot=False):
#     NEODefaultFrame,ABeltDefaultFrame,MSSODefaultFrame,OSSODefaultFrame =None, None, None, None
#     if NightBefore:
#         date-=1
    
#     if BirdsEye :
        
#         NEODefaultFrame   = BirdsEyeViewPlotter(0,2,date,title = 'Near Earth Detections',filename='./Defaults/NearEarthDetections-bev',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
#         MSSODefaultFrame  = BirdsEyeViewPlotter(6,25,date,title = 'Mid Solar System Detections',filename='./Defaults/MidSolarSystemDetections-bev',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
#         ABeltDefaultFrame = BirdsEyeViewPlotter(2,6,date,title = 'Asteroid Belt Detections',filename='./Defaults/AsteroidBeltDetections-bev',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
#         OSSODefaultFrame  = BirdsEyeViewPlotter(25,100,date,title = 'Outer Solar System Detections',filename='./Defaults/OuterSolarSystemDetections-bev',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
     
#     if HistogramPlot:
#         NEODefaultFrame   = HistogramPlot2D(0,2,date,title = 'Near Earth Detections',filename='./Defaults/NearEarthDetections-2DHist',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
#         MSSODefaultFrame  = HistogramPlot2D(6,25,date,title = 'Mid Solar System Detections',filename='./Defaults/MidSolarSystemDetections-2DHist',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
#         ABeltDefaultFrame = HistogramPlot2D(2,6,date,title = 'Asteroid Belt Detections',filename='./Defaults/AsteroidBeltDetectiom-2DHist',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
#         OSSODefaultFrame  = HistogramPlot2D(25,100,date,title = 'Outer Solar System Detections',filename='./Defaults/OuterSolarSystemDetections-2DHist',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
    
#     if HexbinPlot :
#         NEODefaultFrame   = HexPlot(0,2,date,title = 'Near Earth Detections',filename='./Defaults/NearEarthDetections-hexbin',DataFrame = NEODefaultFrame,KeepData=True,ShowPlot=ShowPlot) 
#         MSSODefaultFrame  = HexPlot(6,25,date,title = 'Mid Solar System Detections',filename='./Defaults/MidSolarSystemDetections-hexbin',DataFrame = MSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)
#         ABeltDefaultFrame = HexPlot(2,6,date,title = 'Asteroid Belt Detections',filename='./Defaults/AsteroidBeltDetections-hexbin',DataFrame = ABeltDefaultFrame,KeepData=True,ShowPlot=ShowPlot)
#         OSSODefaultFrame  = HexPlot(25,100,date,title = 'Outer Solar System Detections',filename='./Defaults/OuterSolarSystemDetections-hexbin',DataFrame = OSSODefaultFrame,KeepData=True,ShowPlot=ShowPlot)        
              
#run_plot_defaults(True,True,True,date = 60042,NightBefore=False,ShowPlot=False)


# In[ ]:





# In[ ]:




