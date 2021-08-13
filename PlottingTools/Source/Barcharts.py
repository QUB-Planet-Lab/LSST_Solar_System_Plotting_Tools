from Functions import *
import DataAccessLayer as dal
def HelioDistHist(date=None,day=None,month=None,year=None,title='', 
                  filename=None,DateInterval = 7 ,KeepData=False,ShowPlot=True,
                  DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
    
   
    
    startdate, enddate, title = VariableTesting(0,0,date,day,month,year,title,DateInterval)
    dates = np.linspace(0,DateInterval-1,DateInterval)
    counters = np.ndarray((len(dates)*len(DistanceMinMax),3))
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1))
       


    if DateInterval > 7:
        OutputDF=ps.DataFrame()
        i=0
        while i < (DateInterval // 7):
            if filename is not None: 
                filename += '-'+str(i+1)
            if KeepData:
                OutputDF = ps.concat([OutputDF,HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),7,
                          KeepData,ShowPlot,DistanceMinMax,LogY)])
            else:
                HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),7,
                          KeepData,ShowPlot,DistanceMinMax,LogY)
            i+=1
        if (DateInterval % 7) !=0:
            if KeepData:
                OutputDF = ps.concat([OutputDF,HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),(DateInterval % 7),
                          KeepData,ShowPlot,DistanceMinMax,LogY)])
                    
            else:
                HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),(DateInterval % 7),
                          KeepData,ShowPlot,DistanceMinMax,LogY)
        if KeepData: return OutputDF
        else : return
    count=0
    
    
    for i,offset in enumerate(dates):
        distances = []    
        for MinMax in DistanceMinMax:
            distances+=[[startdate+offset, startdate+offset+1, *MinMax,3]]
            
            
        for j in range(len(distances)):
            df = Queries(*distances[j])
            counters[count,:] = [offset+startdate,df['count'].values[0],j]
            count += 1
    
    NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
    legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
    fig = plt.subplots(figsize=(3*DateInterval,4))
    ax = sns.barplot(x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'])
    ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
    
    
    xval = -0.5
    numberofdistances=0
    xvalcount = 0
    for i,patch in enumerate(ax.patches):
        
        patch.set_width(1/len(distances))
        patch.set_x(xval+numberofdistances)
        xval+=1
        plt.axvline(xval,color='black')
        xvalcount+=1
        if xvalcount==DateInterval:
            xvalcount=0
            xval=-0.5
            numberofdistances+=1/len(distances)
        
    
    ax.set_xticks(ticks[:DateInterval])
    ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in dates+startdate]
    ax.set_xticklabels(ProperDateLabels)
    if LogY:
        ax.set(yscale="log")
    if (filename is not None):
        SavePlot(filename, dict(),ShowPlot)
    else:
        SavePlot(title+'-heliodisthist' ,dict(),ShowPlot)
    if (KeepData == True):
        return NewData        

        
def MonthlyHelioDistHist(date=None,day=None,month=None,year=None,title='', 
                         filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True,
                         DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
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
            counters[count,:] = [startdate,df['count'].values[0],j]
            count += 1
    #Dates+=[DateorMJD(MJD=enddate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
    Dates = [Months[int(date.split('-')[1])-1] + ', '+date.split('-')[0] for date in Dates]
    NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
    rows = (DateInterval // 6)
    if DateInterval % 6 !=0 :
        rows+=1
    fig,axes = plt.subplots(rows,1,figsize=(18,4*rows))
    if rows>1:
        i=0
        count=DateInterval
        while i<rows:

            ax =sns.barplot(data=NewData[i*6*len(DistanceMinMax):(i+1)*6*len(DistanceMinMax)],x='Date',y='Detections',hue='distance',ax=axes.flatten()[i])
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
            while len(Dates[i*6:]) < len(ticks):
                Dates+=['']

            xval = -0.5
            numberofdistances=0
            xvalcount = 0
            for g,patch in enumerate(ax.patches):
                patch.set_width(1/len(distances))
                patch.set_x(xval+numberofdistances)
                xval+=1
                ax.axvline(xval,color='black')
                xvalcount+=1
                limit = len(NewData[i*6*len(DistanceMinMax):(i+1)*6*len(DistanceMinMax)])/len(NewData['distance'].unique())
                if xvalcount== limit :
                    xvalcount=0
                    xval=-0.5
                    numberofdistances+=1/len(distances)
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1))
            ax.set_xticks(ticks[0:6])
            ax.set_xticklabels(Dates[i*6:(i+1)*6],fontsize=20)
            legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
            ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.tick_params(axis='both', labelsize=20)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            plt.tight_layout()
            if i!=0: ax.get_legend().remove()
            if LogY:
                ax.set(yscale="log")
            i+=1
    else:
        ax = sns.barplot(data=NewData,x='Date',y='Detections',hue='distance')
        ax.set_xticks(ticks)
        ax.set_xticklabels(Dates[0:7])
        if LogY:
            ax.set(yscale="log")
        xval = -0.5
        numberofdistances=0
        xvalcount = 0
        for g,patch in enumerate(ax.patches):
                patch.set_width(1/len(distances))
                patch.set_x(xval+numberofdistances)
                xval+=1
                ax.axvline(xval,color='black')
                xvalcount+=1
                
                
                limit = len(NewData)/len(NewData['distance'].unique())
                if xvalcount== limit :
                    xvalcount=0
                    xval=-0.5
                    numberofdistances+=1/len(distances)

        
def YearlyHelioDistHist(date=None,day=None,month=None,year=None,title='', 
                         filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True,
                         DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):

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
    NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
    rows = (DateInterval // 4)
    if DateInterval % 4 !=0 :
        rows+=1
    
    fig,axes = plt.subplots(rows,1,figsize=(12,4*rows))
    if rows>1:
        i=0
        count=DateInterval
        while i<rows:
            ax =sns.barplot(data=NewData[i*4*len(DistanceMinMax):(i+1)*4*len(DistanceMinMax)],x='Date',y='Detections',hue='distance',ax=axes.flatten()[i])
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
            print(len(ticks),ticks,len(Dates),Dates)
            while len(Dates[i*4:]) < len(ticks):
                Dates+=['']

            xval = -0.5
            numberofdistances=0
            xvalcount = 0
            for g,patch in enumerate(ax.patches):
                if i == 2:
                    print(patch)
                patch.set_width(1/len(distances))
                patch.set_x(xval+numberofdistances)
                xval+=1
                ax.axvline(xval,color='black')
                xvalcount+=1
                limit = len(NewData[i*4*len(DistanceMinMax):(i+1)*4*len(DistanceMinMax)])/len(NewData['distance'].unique())
                if xvalcount== limit :
                    xvalcount=0
                    xval=-0.5
                    numberofdistances+=1/len(distances)
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1))
            ax.set_xticks(ticks[0:4])
            ax.set_xticklabels(Dates[i*4:(i+1)*4],fontsize=20)
            legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
            ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.tick_params(axis='both', labelsize=20)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            plt.tight_layout()
            if i!=0: ax.get_legend().remove()
            if LogY:
                ax.set(yscale="log")
            i+=1
    else:
        legend = ["{:.2f}".format(round(distance[2],2))+'-'+"{:.2f}".format(round(distance[3],2))+' (au)' for i,distance in enumerate(distances)]
        ax =sns.barplot(x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'],)
        ax.set_xticks(ticks)
        ax.set_xticklabels(Dates)
        ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
        if LogY:
            ax.set(yscale="log")
        xval = -0.5
        numberofdistances=0
        xvalcount = 0
        for i,patch in enumerate(ax.patches):

            patch.set_width(1/len(distances))
            patch.set_x(xval+numberofdistances)
            xval+=1
            plt.axvline(xval,color='black')
            xvalcount+=1
            if xvalcount==len(NewData)/len(NewData['distance'].unique()):
                xvalcount=0
                xval=-0.5
                numberofdistances+=1/len(distances)

                
                
                
def Weekly24hrHist(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='', filename=None,DateInterval = 7,ShowPlot=True):
    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
     
    dates = np.linspace(0,DateInterval-1,DateInterval)
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1)-0.5)
    counters = np.ndarray((2,len(dates)))

    for i,offset in enumerate(dates):
           
        df = Queries(startdate+offset,startdate+offset+1,mindistance,maxdistance,3) 
        counters[:,i] = [offset+startdate,df['count'].values[0]]
    
    ax = sns.barplot(x=counters[0,:],y=counters[1,:],color='#4ad27a')
    ax.set_xticks(ticks)
    ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in counters[0,:]]

    ax.set_xticklabels(ProperDateLabels+[DateorMJD(MJD=enddate,ConvertToIso=False).to_value(format='iso',subfmt='date')],horizontalalignment='left',rotation=-40)
    ax.tick_params(axis='both', labelsize=16)
    plt.ylabel('Number of Objects Detected over 24Hr')
    plt.xlabel('Date')
    plt.suptitle('Number of Objects')
    for i,patch in enumerate(ax.patches):
        patch.set_width(1)
        patch.set_x(patch.get_x()-0.1)
    
    
    if (filename is not None):
        SavePlot(filename, dict(),ShowPlot)
    else:
        SavePlot(title+'-24hrHist' ,dict(),ShowPlot)
        
     