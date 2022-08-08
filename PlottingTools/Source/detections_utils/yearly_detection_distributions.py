import sys

sys.path.append("../Source")

from Functions import Queries, DateorMJD

import warnings
from plots import BarPlot

import numpy as np
import pandas as pd

from astropy.time import Time
from typing import Optional

def yearly_detection_distributions(
    date=None,
    day=None,
    month=None,
    year=None,
    title='', 
    filename = None,
    DateInterval = 8,
    DistanceMinMax=[[80,81]],
    LogY=True,
    cache_data: Optional[bool] = True
):
    
    with warnings.catch_warnings():
        #dubious year warning
        warnings.filterwarnings("ignore")
        date = DateorMJD(MJD=date,Day=day,Month=month,Year=year,ConvertToIso=False).to_value(format='iso',subfmt='date').split('-')

        counters = np.ndarray((DateInterval*len(DistanceMinMax),3))

        ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
        count=0
        Dates = []


        for i in range(0,DateInterval):
            startdate =Time('-'.join(date)).to_value('mjd')
            Dates+=[DateorMJD(MJD=startdate,ConvertToIso=False).to_value(format='iso',subfmt='date')]

            date[0] = str(int(date[0])+1)
            enddate =Time('-'.join(date)).to_value('mjd')
            distances = []
            for MinMax in DistanceMinMax:
                distances+=[[startdate+0.75, enddate+0.75, *MinMax,3]]
            for j in range(len(distances)):
                df = Queries(*distances[j])
                counters[count,:] = [startdate,df['count'].values[0],j]
                count += 1

        Dates = [ '-'.join(date.split('-')[0:1]) for date in Dates]
        NewData =  pd.DataFrame(data=counters, columns=['Date','Detections','distance'])

        ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
        rows = (DateInterval // 4)
        if DateInterval % 4 !=0 :
            rows+=1

        legend = ["{:.2f}".format(round(distance[2],2))+'-'+"{:.2f}".format(round(distance[3],2))+' (au)' for i,distance in enumerate(distances)]

    bp = BarPlot(data = NewData, x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'], cache_data = cache_data, title = title)
    
    bp.ax.set_xticks(ticks)
    bp.ax.set_xticklabels(Dates)
    bp.ax.legend(handles=bp.ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)

    if LogY:
        bp.ax.set(yscale="log")
    xval = -0.5
    numberofdistances=0
    xvalcount = 0
    for i,patch in enumerate(bp.ax.patches):
        patch.set_width(1/len(distances))

        patch.set_x(xval+numberofdistances)
        xval+=1
        bp.ax.axvline(xval,color='black')
        xvalcount+=1
        if xvalcount==len(NewData)/len(NewData['distance'].unique()):
            xvalcount=0
            xval=-0.5
            numberofdistances+=1/len(distances)
    return bp
