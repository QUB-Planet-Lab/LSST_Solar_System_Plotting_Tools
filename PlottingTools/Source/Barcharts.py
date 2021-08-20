from Functions import *
import DataAccessLayer as dal

## HelioDistHist: This is a set of bar charts for a user set distance range of heliocentric distances with data for every day within the user set date range. 

## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ask the user to explicitly specify the filename 
## DateInterval: This is how long you want to query about the date set above, -1 would be the 24 hours before the set date.
##               +1 would be 24 hours after set date (float), behaviour changed and now defaults to +1 date, this allows
##               this will allow you to alter the behaviour of the function and go forward or backword in time.
## KeepData: Used to keep query data in DataFrame Object that is returned from the function as this allows a reduction of
##           Queries to the database. (boolean)
## Showplot: This dictates whether the plot is closed or not after running the function, this is here to manage command
##           line behaviour where open plot figures can cause issues with preventing code from continuing to run. whilst
##           allowing this to be set to false so that figures are shown in Notebook form.
## DistanceMinMax: Is a list of lists and is a variable that takes in the user defined distance ranges.so each list item is a list that contains an upper and lower bound 
##                 for example [0,2] is a value list item and if the user only wants one distance range then the parameter input would be [[0,2]], usually in python it can be discouraged
##                 to use lists in input, however at no point does these lists or any other get appended or mutated and are not subject to problems with input parameter mutation
##                 As such if DistanceMinMax were changed to say append [5,10] internally within the function the next time that function is called then the default would be mutated.
## LogY: LogY is a boolean variable that designates whether the user wants the number of detections in a Logarithmic scale, this can be useful to turn off for small numbers of 
##        objects.

def HelioDistHist(date=None,day=None,month=None,year=None,title='', 
                  filename=None,DateInterval = 7 ,KeepData=False,ShowPlot=True,
                  DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
    
   
    #Calls Variable testing which will check that title can be cast as a string and calculates the start and end date using the Date Interval value.
    startdate, enddate, title = VariableTesting(0,0,date,day,month,year,title,DateInterval)
    ## dates is an np array with equally spaced elements with the number of elements being the DateInterval so length of your date range. 
    dates = np.linspace(0,DateInterval-1,DateInterval)
    ## Counters is used to help build the pandas DataFrame you will return to to user/ also use to plot the data
    counters = np.ndarray((len(dates)*len(DistanceMinMax),3))
    ## Ticks is a list of values that are used to change the tick positions on the graph if necessary, as you can then add extra ticks and labels if necessary. 
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1))
       

    ## So if the DateInterval is greater than 7 then we go into a recursive loop, As someone may want the daily detections for a year and overflowing to say the next row on a plot
    ## would quickly become a foolish option as you would destroy the ability to read the graphs as for a year you would already have 52 rows, as such if the DateInterval is greater
    ## than a week we then create a OutputDF can we can still keep all the relavant data from the queries to return to the user if they so wish.
    if DateInterval > 7:
        OutputDF=ps.DataFrame()
        ## At the start of this while loop we set i=0 and have it set so i< (DateInterval // 7) which checks how many times 7 goes into DateInterval so say DateInterval is 24 then
        ## DateInterval // 7 would be 3 and as i starts at 1 we then use less than and iterate i+=1 for each iteration in the while loop, ie, i=0,1,2 for DateInterval =24 
        i=0
        while i < (DateInterval // 7):
          ## As you cannot use the same filename eachtime we have to build in a method to prevent overwritting the plots so if the filename is not none then we add a numerical 
          ## affix to denote them uniquely
          ## NEED to check this, there may be accidental mutation of the filename.
            if filename is not None: 
                filename += '-'+str(i+1)
            ## If the user wants the data returned then we append it to a DataFrame within the function and build it up, otherwise theres no need to keep the data in memory.
            if KeepData:
              ## Concatinates the two dataframes and then sets them OutputDF to the result.
                OutputDF = ps.concat([OutputDF,HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),7,
                          KeepData,ShowPlot,DistanceMinMax,LogY)])
            else:
              ## Otherwise there is no need to keep the dataframe and it is released to the GC
                HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),7,
                          KeepData,ShowPlot,DistanceMinMax,LogY)
            ## i is incremented each time in the while loop
            i+=1
        ## In the first while loop we checked how many full times 7 went into DateInterval, but now we need to check for the remainder in order to add those aswell.
        ## So if the remainder is non zero then we run the function one more time for the remainder.
        ## i is once again used to give a unique plot filename. 
        if (DateInterval % 7) !=0:
            ## If KeepData is true then we concatinate the OutputDF with the return from the HelioDistFunction to finish building the DataFrame that can be returned to the user
            if KeepData:
              ## use pandas concatination to add the dataframes vertically. with the function call being a call to the same function so that it can handle the DB call and get the 
              ## query result with the data the user already entered.
                OutputDF = ps.concat([OutputDF,HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),(DateInterval % 7),
                          KeepData,ShowPlot,DistanceMinMax,LogY)])
                    
            else:
              #Calls the function with user set parameters with DateInterval set to the remainder to get the correct number of days.
                HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename+' Plot #'+str(i+1),(DateInterval % 7),
                          KeepData,ShowPlot,DistanceMinMax,LogY)
        # If KeepData is true then it returns the built DataFrame, otherwise it returns a None object
        if KeepData: return OutputDF
        else : return
    count=0
    
    # We then enumerate through the dates for a for loop for the DateInterval Number of days
    for i,offset in enumerate(dates):
      # we set the distances list to empty
        distances = []    
        # we then use the each MinMax pair in the DistanceMinMax list to build a list of lists in the distances list which contains the information for the queries function
        for MinMax in DistanceMinMax:
            distances+=[[startdate+offset, startdate+offset+1, *MinMax,3]]
            
        # we then do a if for each distance range per day, with df being a single days query for a single distance and we do each element within distances    
        for j in range(len(distances)):
            df = Queries(*distances[j])
            # we then build an np multidimensional array in counters with the columns being the date,the number of detections as it will always be the first element of the count
            # column and then we use j to denote which of the distances it relates to, ie 0,1,2 and if the distances are [[0,2],[2,4],[4,6]] then the 0 maps to 0,2 etc etc 
            counters[count,:] = [offset+startdate,df['count'].values[0],j]
            #we then increase the count to go to the next row for the next query. 
            count += 1
    #Create a new dataframe with the data as the np array we generated earlier, and set the column names as well. 
    NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
    # Now we need to generate the legend names for as with the current columns they will show as 0,1,2 instead of the values they are, as such we use a list comprehension to create
    # the list that will be the legend labels, with units added as well
    legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
    # We then create a figure, which scales with the number of days of survey so that the aspect ration is locked
    fig = plt.subplots(figsize=(3*DateInterval,4))
    # we then create the bar plot using our new DataFrame, with x being our date, y being the number of detections and the hue being set by the distance range 
    ax = sns.barplot(x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'])
    # we then update the legend labels with the ones we generared from the distance array so they appear on the plot
    ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
    
    # As we are using seaborn it is difficult to pass a width parameter for the bars, as such they fill 0.8 of the width that they should.
    # we then use x,val,numberofdistances and xvalcount to retify this.
    xval = -0.5
    numberofdistances=0
    xvalcount = 0
    # here we enumerate through the patches on the the axis,
    for i,patch in enumerate(ax.patches):
       # we set the width of the bars to take an equal area each whilst filling their area, but typically due to their changing size they need shifted
        patch.set_width(1/len(distances))
        # xval is set to the negative -0.5 offset we put on patches such as rectangles on the barchart
        # we then add +1 to xval each iteration so the bars do not overlap for each distance.
        patch.set_x(xval+numberofdistances)
        xval+=1
        # This adds a vertical line after each day which allows easier comparison
        plt.axvline(xval,color='black')
        # we increase xvalcount as we have to reset it to 0 after the date interval as say if you have 4 distances and 7 Days of data then there are 28 Patches on the axes
        # however you need to then reset that to 0, for the next distance range as each distance range is done once at a time, you then add an offset called number of distances which
        # is the fraction of 1 the bar should take up so the next distance range can be shifted over by that so they do not overlap.
        xvalcount+=1
        if xvalcount==DateInterval:
            xvalcount=0
            xval=-0.5
            numberofdistances+=1/len(distances)
        
    # We then set the xticks to ensure we have the exact number we want.
    ax.set_xticks(ticks[:DateInterval])
    # We then set the labels to proper date labels instead of the modified julian date to make it easier to use.
    # This is once again achieved by using a list comprehension to build the list of values.
    ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in dates+startdate]
    ax.set_xticklabels(ProperDateLabels)
    # If the user wants a logarithmic scale then this will set the axis to logarithmic
    if LogY:
        ax.set(yscale="log")
    # Here we save the plot  using either the filename if the user has added one or we use the title and a appropriate affix to build a useful name, we use the SavePlot in Functions.Py
    # to do this.
    if (filename is not None):
        SavePlot(filename, dict(),ShowPlot)
    else:
        SavePlot(title+'-heliodisthist' ,dict(),ShowPlot)
    # If the user asked to keep the data with having KeepData be a True boolean then we return the dataframe to the user, 
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
        
     
