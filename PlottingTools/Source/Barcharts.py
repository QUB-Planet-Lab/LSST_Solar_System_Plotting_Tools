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

## MonthlyHelioDistHist: This is a set of bar charts for a user set distance range of heliocentric distances with data for every day within the user set date range. 

## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ask the user to explicitly specify the filename 
## DateInterval: DateInterval works slightly differently here, the query automatically defaults to the first of a month and the date interval in this case refers to the number of 
##               months that should be shown.
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
def MonthlyHelioDistHist(date=None,day=None,month=None,year=None,title='', 
                         filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True,
                         DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
    #Here we set out a list of our months that we will use to index when setting the plot labels later
    Months = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    # So we then get then parse the date and return it as a list so we have day,month,year components if given in MJD
    date = DateorMJD(MJD=date,Day=day,Month=month,Year=year,ConvertToIso=False).to_value(format='iso',subfmt='date').split('-')
    #We then set the day of the month to the first.
    date[-1] = '01'
    #As we did in the previous function we set up the counters array which will hold our counted results with it being set size wise as number of Months *number of Distances ranges
    # as we need to take both in account to have the right length. 
    counters = np.ndarray((DateInterval*len(DistanceMinMax),3))
    #we set up the ticks list that is equally spread out between 0 and number of months -1, this will then allow us to set the ticks to center and then change the tick labels at the
    # same time.
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
    count=0
    #We initialize an empy Dates list
    Dates = []
    #We start a for loop and run it the sane number of times as the date interval as we need to do this once for every date.
    for i in range(0,DateInterval):
        #We firstly convert the date to mjd.
        startdate =Time('-'.join(date)).to_value('mjd')
        #we then add this date to the Dates List so we have it collected for when we convert to Months in words when we need to add labels for months later.
        Dates+=[DateorMJD(MJD=startdate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
        #Here we check if the Month is the 12th ie december and if it is then we roll it over to a new year and set the month to 1
        # otherwise we just add one to the months
        # it is useful to note that if the month is less than 10 then we prepend a zero to keep in line with the expected iso date formate for day,month and year.
        if int(date[1]) ==12:
            date[0] = str(int(date[0])+1); 
            date[1] = '01'
        else:
            date[1] = str(int(date[1])+1)
            if int(date[1]) <10:
                date[1] = '0'+date[1]
        # We then use the new date to calculate the end date having incremented the month by 1 so we now have the start date say 1st January and end date, say 1st February 
        enddate =Time('-'.join(date)).to_value('mjd')
        # Now we then need to create the distances list which will be a list of lists containing all the information for each query for that month for each distance range.
        # MinMax is the heliocentric lower and upper bound values for each distance range within the DistanceMinMax List of lists.
        distances = []
        for MinMax in DistanceMinMax:
            distances+=[[startdate+0.75, enddate+0.75, *MinMax,3]]
        # Once we have built the distances list we then iterate through it in a for loop to query the database and save the query results and identifying information in the counters
        # array. We then increase the count by one as it keeps track on where we are in the overall progress, ie count goes from 0 to (DateInterval*Number of Distance Ranges)-1 and
        # is used to index the counters array to prevent overwritting, we avoid using a pandas dataframe and appending as it is quite a slow operation in pandas.
        for j in range(len(distances)):
          #Here we use the Queries function to deal with the query and calling the database to handle the Query.
            df = Queries(*distances[j])
            # Number of objects is saved in counters, alongside the start date and j which will tell the distance it relates to as j goes from 0,1,2 if there are 3 distance ranges etc.
            counters[count,:] = [startdate,df['count'].values[0],j]
            count += 1
    #Dates+=[DateorMJD(MJD=enddate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
    # Here we replace the start dates with the month in words and the year so the data is labelled easily
    Dates = [Months[int(date.split('-')[1])-1] + ', '+date.split('-')[0] for date in Dates]
    # We then create a dataframe from the counters array using our set column titles so we know their keys.
    NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
    # We then do the // and % checks to roll over to a next row when there are more than 6 months of data and check the remainder to ensure that all data is plotted in the correct
    # way.
    rows = (DateInterval // 6)
    if DateInterval % 6 !=0 :
        rows+=1
    # We then set the size of the figure based on number of rows to maintain a nice aspect for the user 
    fig,axes = plt.subplots(rows,1,figsize=(18,4*rows))
    # If the number of rows is greater than one then we need to plot on a number of difference axes so we then use a while looped that checks the condition at the start 
    
    if rows>1:
        i=0
        count=DateInterval
        # as we use i as initially being equal to 0 then we can use it to index to the correct axis aswell as using less than operator to exit at the correct point. 
        while i<rows:
            #on the axes we plot a barplot by using the pandas dataframe we made earlier, however we need to slice it so that we only plot the correct data for this axis
            # ie the first 6 months and ensure that the 7th month isn't accidentially plotted instead, so how do we slice it correctly? well for the first row i =0 so it indexes from
            # 0 to 6(width of each row)* length of DistanceMinMax which is the number of distance ranges, this works as the upper slice is not inclusive so we only plot the correct data.
            ax =sns.barplot(data=NewData[i*6*len(DistanceMinMax):(i+1)*6*len(DistanceMinMax)],x='Date',y='Detections',hue='distance',ax=axes.flatten()[i])
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
            #so for when i is not zero we might find where we may not fill the row but we have ticks for the whole row in order to preserve the aspect ration so we then need to add
            # list elements to bring them to the same length so we just pad dates with empty string list elements.
            while len(Dates[i*6:]) < len(ticks):
                Dates+=['']
            # this works similarly to in the previous function where we make the width of each bar be the full width of what it could be instead of being 0.8 of the available area
            # we then recenter the rectanges which are patches on the graph so that they do not overlap.
            xval = -0.5
            numberofdistances=0
            xvalcount = 0
            # So here what we do is we iterate through each patch and we make it the right width and put it in the right position with set_width and set_x, we do this for each distance
            # range one at a time as each distance ranges needs a offset added so that they do not overlap with eachother. 
            for g,patch in enumerate(ax.patches):
                patch.set_width(1/len(distances))
                patch.set_x(xval+numberofdistances)
                xval+=1
                #We add a vertical line to make it east to distinguish between months, we set this only by xval as we only need it per month, not per distance range.
                ax.axvline(xval,color='black')
                xvalcount+=1
                #We then set a limit based on the number of Months of data there is and reset and increment the number of distances so we can address each distance range.
                limit = len(NewData[i*6*len(DistanceMinMax):(i+1)*6*len(DistanceMinMax)])/len(NewData['distance'].unique())
                if xvalcount== limit :
                    xvalcount=0
                    xval=-0.5
                    numberofdistances+=1/len(distances)
             
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1))
            # We then set the ticks and Monthly in words with year date labels in this two following lines, we set the fontsize at 20 to make it nice and noticable on the large plot
            ax.set_xticks(ticks[0:6])
            ax.set_xticklabels(Dates[i*6:(i+1)*6],fontsize=20)
            # We then build a legend labels based on the upper and lower bound of the heliocentric distance using a list comprehension
            legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]
            # and we then apply this legend labels using the same handles already made as we have a partial legend from 'hue' has we had distances 0,1,2 etc and we replace that with their
            # actual values now. we also move the legend box off the plot to prevent it from blocking data points etc.
            ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
            # We make the labels large for easy viewing 
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            # we do the same for tick params also to ensure nothing is left showing small on the plot or saved image.
            ax.tick_params(axis='both', labelsize=20)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            # We use tight_layout() as it prevents the plots from overlapping the labels as this can happen if not explicitly preventeded.
            plt.tight_layout()
            # We then check if i is not equal to one and remove the legend on that axis as it is useless to have it for the second and third row as it is already there.
            if i!=0: ax.get_legend().remove()
            # Here we check if the user wants the plot in Logarithmic form on the y as this is idealy the most useful representation for a monthly object detection plot.
            if LogY:
                ax.set(yscale="log")
            #We then increment i by one and move to the next step of the loop or exit based on the i< rows condition.
            i+=1
    else:
      #This is where there is only a single row so 6 or less months, we can plot using all the data
        ax = sns.barplot(data=NewData,x='Date',y='Detections',hue='distance')
        #we then set the ticks and dates, and we don't have to pad it in this as we only have a single row.
        ax.set_xticks(ticks)
        ax.set_xticklabels(Dates[0:7])
        #We then check whether the axes need to be log based on the user input
        if LogY:
            ax.set(yscale="log")
            #we then undertake the same repositioning of the rectangle patches on the bar chart as shown just before the else statement. 
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

## YearlyHelioDistHist: This is a set of bar charts for a user set distance range of heliocentric distances with data for each year within the user set date range. 

## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ask the user to explicitly specify the filename 
## DateInterval: This is how long you want to query about the date set above, as this is the yearly function the date interval increments in years instead of days and months like the previous
##               functions.
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
        
def YearlyHelioDistHist(date=None,day=None,month=None,year=None,title='', 
                         filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True,
                         DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
    # We convert either the MJD or Day,Month,Year to an MJD value
    date = DateorMJD(MJD=date,Day=day,Month=month,Year=year,ConvertToIso=False).to_value(format='iso',subfmt='date').split('-')

    ## We set up the counters to be 3 columns with length being the product of the date interval ie number of years and the length of DistanceMinMax which gives the number of distance
    ## ranges so we have space for each result in the array
    counters = np.ndarray((DateInterval*len(DistanceMinMax),3))
    ## Like in the previous functions we set up an array which will be used to specifically place the ticks onto the plot later.
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
    count=0
    #We create an empty Dates list. this will be used to build an list of labels for the plot later on in the function
    Dates = []
    ## So we iterate for each year, in this loop, it works by iterating for a each, building the query for each distance range and then querying the database for each distance range
    ## we then add that to a row of a numpy array and then iterate through the next year.
    for i in range(0,DateInterval):
        # We calculate the start date from the date and put it in modified julian date.
        startdate =Time('-'.join(date)).to_value('mjd')
        #We then append this start date to the Dates list and this will be used for the labels on the plots.
        Dates+=[DateorMJD(MJD=startdate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
        # we then increment the modified julian date by 1 as that corresponds to the next year, we then once again use the date to create the enddate aswell now that it represents the next year.
        
        date[0] = str(int(date[0])+1)
        enddate =Time('-'.join(date)).to_value('mjd')
        # we then create an empty distances array and we will use the distance array for the arguments that go to the query in the next for loop.
        distances = []
        # this for loop is used. to generate the distance array from the DistanceMinMax list of lists where the MinMax is a List item containing the lower and upper bound of the user set
        # distance range. the +0.75 on the start date and end date bring the time to 18:00 utc so that queries catch an entire nights worth of data. this is less of an issue for yearly
        # queries but for the sake of accuracy is included to be consistent with the other functions.
        for MinMax in DistanceMinMax:
            distances+=[[startdate+0.75, enddate+0.75, *MinMax,3]]
        # we iterate through each list item in the distance array and query the database using them and then add the results to the counters array with the first column being
        # the startdate, the 'count' of the number of objects being the second and the third being j which is used to differentiate between the different distances.
        for j in range(len(distances)):
            df = Queries(*distances[j])
            counters[count,:] = [startdate,df['count'].values[0],j]
            count += 1
    
    # Here we strip off the day and month from the date in iso form so that we are only left with the year of the data, the data starts of the 1st of January of each year.
    Dates = [ '-'.join(date.split('-')[0:1]) for date in Dates]
    # We then generate a dataframe the the counters numpy array and set the column names to Date,Detections and Distance as these are keys we know.
    NewData =  ps.DataFrame(data=counters, columns=['Date','Detections','distance'])
    
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
    # Now we need to calculate such that there are only 4 years per row, and if it is greater than that then roll over to the next row, we do that using // and % as that tells us how many
    ## times it gos through 4 and then the remainer.
    rows = (DateInterval // 4)
    if DateInterval % 4 !=0 :
        rows+=1
    # We set up our sub plots and we set the figsize to the correct aspect ratio. with one plot per row and the number of rows is set to rows
    fig,axes = plt.subplots(rows,1,figsize=(12,4*rows))
    # If the number of rows is >1 then we need to slice the data to only plot the correct data on each row.
    if rows>1:
        i=0
        count=DateInterval
        while i<rows:
          # We put the plot on the correct axis using i. we slice the data using i*4*(number of distance ranges):(i+1)*4*(number of distance ranges) this allows use to split the data
          # for each row and only plot the correct data. 
            ax =sns.barplot(data=NewData[i*4*len(DistanceMinMax):(i+1)*4*len(DistanceMinMax)],x='Date',y='Detections',hue='distance',ax=axes.flatten()[i])
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
            #print(len(ticks),ticks,len(Dates),Dates)
            # for the second row we need to pad the Dates Array so that the number of ticks and the number of labels are not different to prevent errors so we just add an empty string.
            # until they are of equal length.
            while len(Dates[i*4:]) < len(ticks):
                Dates+=['']
            
            # once again these 3 variables help to resize and recenter the bars that are plotted onto the plot axes as rectangles, we start with xval at -0.5 as that is where the
            # first bar needs to be centered whilst the number of distances refers to the number of MinMax pairs, the xval count is then used to count through the years
            xval = -0.5
            numberofdistances=0
            xvalcount = 0
            # we iterate through each patch on the axis that this contains each one of the objects plotted on the figure.
            # xval effectively operates like the ticks and is incremented by one for each bar on the graph for a single distance.
            # so this iterates through, does one distance and sets the width and the x value and then it moves onto the next distance by reseting the values 
            for g,patch in enumerate(ax.patches):
                #if i == 2:
                #    print(patch)
                # set the width of the patch to 1/ the number of distances such that each takes up an equal area of the figure.
                patch.set_width(1/len(distances))
                # we set the x value of the rectangular patch using xval which relates to which year we are talking about and then with the offset from the number of distances
                # ie for 4 different distance ranges you would get your 4 different offsets so that they do not overlap.
                patch.set_x(xval+numberofdistances)
                # we then increment the xval by one for the next year, add a vertical line to deliniate between lines and then check if the xvaluecount after being incremented
                # by 1 has hit the limit of the number of years to see if we need to reset the variables and move onto the next distance range.
                xval+=1
                ax.axvline(xval,color='black')
                xvalcount+=1
                limit = len(NewData[i*4*len(DistanceMinMax):(i+1)*4*len(DistanceMinMax)])/len(NewData['distance'].unique())
                if xvalcount== limit :
                    xvalcount=0
                    xval=-0.5
                    numberofdistances+=1/len(distances)
            # This ensures we have the correct ticks for the labels on the plot with the ticks going from 0 to the number of years so for 4 years, we have ticks of 0,1,2,3,4
            ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1))
            #we then set the x ticks
            ax.set_xticks(ticks[0:4])
            # we then use the Dates list that was constructed earlier to use slice the Date array based on the row that is being plotted at that time, with this Date being the Year.
            ax.set_xticklabels(Dates[i*4:(i+1)*4],fontsize=20)
            # The legend is then constructed with formatting and rounding done in order to ensure no visual errors on the plot that can be caused by generating MinMax pairs from
            # np.linspace and usage of floating point numbers
            legend = ["{:.2f}".format(round(distance[2],2))+'-'+"{:.2f}".format(round(distance[3],2))+' (au)' for i,distance in enumerate(distances)]
            # this legend text is then added to the figure
            ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
            # This here is just resizing the text labels to make them easy to read.
            ax.xaxis.get_label().set_fontsize(20)
            ax.yaxis.get_label().set_fontsize(20)
            ax.tick_params(axis='both', labelsize=20)
            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticklabels(),fontsize=20)
            # This prevents the overlap of text and the axis plots
            plt.tight_layout()
            # Here we remove the extra legends that get duplicated with the same content multiple times.
            if i!=0: ax.get_legend().remove()
            # And if the user sets so the y scale of the plot is set to logarithmic
            if LogY:
                ax.set(yscale="log")
            # i is iterated to move onto the next row of the figure.
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
        
     
