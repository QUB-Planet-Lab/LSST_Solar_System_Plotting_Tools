import sys 

sys.path.append("../Source")

from Functions import Queries, DateorMJD

import numpy as np
import pandas as pd

from plots import BarPlot

def _daily_detection_distributions(
    start_time,
    end_time,
    DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]]
):
    KeepData = False
    interval = int(end_time) - int(start_time)

    dates = np.linspace(0, interval-1, interval)
    counters = np.ndarray((len(dates)*len(DistanceMinMax),3))

    ticks = np.ndarray.tolist(np.linspace(0, interval,interval+1))

    count=0

    for i,offset in enumerate(dates):
        distances = []    

        for MinMax in DistanceMinMax:
            distances+=[[start_time+offset, start_time+offset+1, *MinMax,3]]

        for j in range(len(distances)):
            df = Queries(*distances[j])

            counters[count,:] = [offset+ start_time,df['count'].values[0],j]

            count += 1

    NewData =  pd.DataFrame(data=counters, columns=['Date','Detections','distance'])

    legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]

    bp = BarPlot(data = NewData, x = "Date", y = "Detections", hue="distance", xlabel = "Date", ylabel = "Detection count")

    bp.ax.legend(handles=bp.ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = .2,)

    xval = -0.5
    numberofdistances=0
    xvalcount = 0
    for i,patch in enumerate(bp.ax.patches):
        patch.set_width(1/len(distances))

        patch.set_x(xval+numberofdistances)
        xval+=1

        bp.ax.axvline(xval,color='black')

        xvalcount+=1

        if xvalcount == interval:
            xvalcount=0
            xval=-0.5
            numberofdistances+=1/len(distances)

    bp.ax.set_xticks(ticks[:interval])

    ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in dates+start_time]

    bp.ax.set_xticklabels(ProperDateLabels)

    bp.ax.set(yscale="log")

    return bp