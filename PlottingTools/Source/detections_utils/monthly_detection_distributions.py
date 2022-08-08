import sys

sys.path.append("../Source")

from Functions import Queries, DateorMJD

from plots import BarPlot

from astropy.time import Time
import numpy as np
import pandas as pd

from typing import Optional

def monthly_detection_distributions(
    date=60042,
    day=None,
    month=None,
    year=None,
    title='', 
    filename=None,
    DateInterval = 2,
    DistanceMinMax=[[80, 81]],
    LogY=True,
    cache_data : Optional[bool] = True
):

    Months = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    
    date = DateorMJD(MJD=date,Day=day,Month=month,Year=year,ConvertToIso=False).to_value(format='iso',subfmt='date').split('-')
    
    date[-1] = '01'

    counters = np.ndarray((DateInterval*len(DistanceMinMax),3))

    ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
    count=0
    Dates = []
    for i in range(0,DateInterval):
        startdate =Time('-'.join(date)).to_value('mjd')
        Dates+=[DateorMJD(MJD=startdate,ConvertToIso=False).to_value(format='iso',subfmt='date')]

        if int(date[1]) ==12:
            date[0] = str(int(date[0])+1); 
            date[1] = '01'
        else:
            date[1] = str(int(date[1])+1)
            if int(date[1]) <10:
                date[1] = '0'+date[1]

        enddate =Time('-'.join(date)).to_value('mjd')

        distances = []
        for MinMax in DistanceMinMax:
            distances+=[[startdate+0.75, enddate+0.75, *MinMax,3]]
        
        for j in range(len(distances)):

            df = Queries(*distances[j])

            counters[count,:] = [startdate, df['count'].values[0],j]
            count += 1
    
    Dates = [Months[int(date.split('-')[1])-1] + ', '+date.split('-')[0] for date in Dates]
   
    NewData =  pd.DataFrame(data=counters, columns=['Date','Detections','distance'])

    
    rows = (DateInterval // 6)
    
    bp = BarPlot(data=NewData,x='Date', y='Detections',hue='distance', cache_data = cache_data, title = title)

    bp.ax.set_xticks(ticks)
    bp.ax.set_xticklabels(Dates[0:7])
    
    legend = ["{:.2f}".format(round(distance[2],2))+'-'+"{:.2f}".format(round(distance[3],2))+' (au)' for i,distance in enumerate(distances)]
    bp.ax.legend(handles=bp.ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)

    if LogY:
        bp.ax.set(yscale="log")
    xval = -0.5
    numberofdistances=0
    xvalcount = 0
    for g,patch in enumerate(bp.ax.patches):
        patch.set_width(1/len(distances))
        patch.set_x(xval+numberofdistances)
        xval+=1
        bp.ax.axvline(xval,color='black')
        xvalcount+=1

        limit = len(NewData)/len(NewData['distance'].unique())
        if xvalcount== limit :
            xvalcount=0
            xval=-0.5
            numberofdistances+=1/len(distances)
    return bp