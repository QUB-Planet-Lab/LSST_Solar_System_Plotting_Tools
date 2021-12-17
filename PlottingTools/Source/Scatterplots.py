from Functions import *
import DataAccessLayer as dal
## Birds Eye View Plotting Function, plots the x-y plane.
## mindistance: Minimum Asteroid Distance from the sun you want in the plot (int) / au
## maxdistance: Maximum Asteroid Distance from the sun you want in the plot (int) / au
## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ally the user to explicitly specify the filename 
## DateInterval: This is how long you want to query about the date set above, -1 would be the 24 hours before the set date.
##               +1 would be 24 hours after set date (float), behaviour changed and now defaults to +1 date, this allows
##               this will allow you to alter the behaviour of the function and go forward or backword in time.
## KeepData: Used to keep query data in DataFrame Object that is returned from the function as this allows a reduction of
##           Queries to the database. (boolean)
## Showplot: This dictates whether the plot is closed or not after running the function, this is here to manage command
##           line behaviour where open plot figures can cause issues with preventing code from continuing to run. whilst
##           allowing this to be set to false so that figures are shown in Notebook form.
## DataFrame: Allows the use of a preprepared dataframe to use in the plots as well as prevents too many queries 
##            on the database
## PlanetsOnPlot: This dictates whether the circular approximation of planetary orbits is plotted on the figures.
## Filters: This is a parameter that should either be left as None to plot all filters on a single graph, or as
##          as a string that contains the names of each of the filters you want plotted, for example:
##          'grizy', 'y','rgy','zyri' are all valid inputs for filters.
def BirdsEyeViewPlotter(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1):
    #This calls a simple Variable Type testing function that also calculates the start and end dates of the query.
    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
    
    # Here the program checks if there has been a DataFrame passed to the function, as if there is then it is used to reduce
    # the number of queries going to the database.
    # If the dataframe is not passed to the program then a Query is made to the database in the Queries function by using the DAL
    
    if(DataFrame is None):
        df = Queries(startdate,enddate,mindistance,maxdistance,QueryNum)
        DataFrame = df.copy(deep=True)
    # The .copy(deep=True) is here to ensure immutability of the data contained, whilst it does force a second DF of 
    # equal size into memory it does allow the data to remain
    ## May need to write df = DataFrame and use copy to ensure the DataFrame that goes in is what comes out as as of right now
    ## This is not the case as df is returned not DataFrame
    else: df = DataFrame.copy(deep=True)    
    
    
    
    ## If the dataframe is empty, ie no results or empty DataFrame passed to the function then a warning is returned to the console, and the function will just return the empty
    ## DataFrame, therefore not generating any plots or figures.
    if df.empty :
        warnings.warn('No Results in this region for this timeframe')
        return df
    
    # We use 'arguments' and 'setplotlabelsandlimits' as dictionaries which are used to set some of the parameters for the plots, we set the marker on the plots to a dot . for 
    # example, in another example we can set the xlabel and ylabel of a plot using these, and as we have repeated but slightly different code, we can store the common elements 
    # in these dictionaries, so that when we change it for when Filters is None condition, it is changed for the other condition, as such we have better mantainability and consistency
    arguments = dict(marker='.',edgecolor=None,hue = df['filter'] )
    
    setplotlabelsandlimits = dict(xlim=[-1*maxdistance,maxdistance],ylim=[-1*maxdistance,maxdistance],xlabel='x (au)',ylabel='y (au)')
    
    if Filters is None:
        #Creates the figure with a set size fixed at (10,10)
        plt.figure(figsize=(10, 10))
        plot = sns.scatterplot(x=df[xyscale[0]],y=df[xyscale[1]],**arguments)
        #Labels the axes so that the user knows
        plot.set(**setplotlabelsandlimits)
        # Plots the sun and planets onto heliocentric plots 
        PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance)
        # sets the title to the user defined title and with the date range added so the user can easily refer to the date.
        plt.title(title+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''))
        
        # grabs the current axes so that a legend can be defined for it.
        ax = plt.gca()
        lgd = ax.legend(loc='upper left', bbox_to_anchor=(1,1), borderpad = 2, )
        # If the user has not defined a filename then a filename is generated using the title, the parameters in the plot on the x and y
        # axis and using a descriptor of the plot ie the '-bev', the legend is also applied to the ploting using a dictionary passed as the
        # extraargs variable of SavePlot.
        if (filename is not None):
            SavePlot(filename ,dict(bbox_extra_artists=(lgd,)),ShowPlot)
        elif title is not None:
            SavePlot(title+'-'+xyscale[2]+'-bev' ,dict(bbox_extra_artists=(lgd,)),ShowPlot)
        
        # This determines whether or not a dataframe is returned from this function or not based on the user set variable 'KeepData'
        # If true then a df is returned, otherwise the dataframe is just left to the python GC which should clean it up once when function 
        # variable space is closed.
        if (KeepData == True):
            return DataFrame
    else:
        # If the user has defined a specific set of filters they want to see for their given distance and date timeframe then
        # this part of the function is triggered which grabs all the filters that are in the queried dataframe.
        filters = df['filter'].groupby(df['filter']).unique()
        # We check through each letter of the unique dataframe filters
        for filter in filters:
            # We then use a regex search to check if the user defined filter matches one of the filters in the dataframe and if it does
            # then it goes through and starts the plotting process.
            if re.search(filter[0],Filters):
              # Here we create a subset of the dataframe with the current filter we are investigating
                currentfilter = df[df['filter']==filter[0]]
                # boolean check to see if the DF is empty of a paticular filter, necessary to prevent any errors from being thrown if the scatterplot data is empty
                if currentfilter.empty:
                    print('Filter '+filter[0] +' has no results for this timeframe.')
                #Creates the figure with a set size fixed at (10,10)
                plt.figure(figsize=(10, 10))
                plot=sns.scatterplot(x=currentfilter[xyscale[0]],y=currentfilter[xyscale[1]],**arguments)
                #Labels the axes so that the user knows what each one refers to
                plot.set(**setplotlabelsandlimits)
                # We set the title of the plot, with a plethora of useful information, usage of DateorMJD is explained in the Function.Py file.
                plt.title(title+' Filter: '+filter[0]+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000','')) 
                # Information on this function is included in Function.Py aswell, however what it does, if the plot is heliocentric, then it plots the planets that are within the range
                # of the data in the plot
                PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance)
                #This code here is gca() just gets current axes, so it will get the most recent axes on your figure and this will allow the legend to be added to the plot.
                ax=plt.gca()
                # We anchor the legend to outside of the figure so that it doesn't overplot on possibly important points 
                lgd = ax.legend(loc='upper left', bbox_to_anchor=(1,1), borderpad = 2, )
                # If the user has not defined a filename then a filename is generated using the title, the parameters in the plot on the x and y
                # axis and using a descriptor of the plot ie the '-bev', the filter name is also used in the filename to distinguish it from the other filters plots.
                #, the legend is also applied to the ploting using a dictionary passed as the
                # extraargs variable of SavePlot.
                
                if (filename is not None):
                    SavePlot(filename +'-'+filter[0] ,dict(bbox_extra_artists=(lgd,)),ShowPlot)
                elif title is not None:
                    SavePlot(title +'-'+filter[0]+'-'+xyscale[2]+'-bev',dict(bbox_extra_artists=(lgd,)),ShowPlot)
        #If the user wants the DataFrame kept in memory for usage in other funtion calls, this if statement returns it for them.        
        if (KeepData == True):
            return DataFrame
    


## mindistance: Minimum Asteroid Distance from the sun you want in the plot (int) / au
## maxdistance: Maximum Asteroid Distance from the sun you want in the plot (int) / au
## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ally the user to explicitly specify the filename 
## DateInterval: This is how long you want to query about the date set above, -1 would be the 24 hours before the set date.
##               +1 would be 24 hours after set date (float), behaviour changed and now defaults to +1 date, this allows
##               this will allow you to alter the behaviour of the function and go forward or backword in time.
## KeepData: Used to keep query data in DataFrame Object that is returned from the function as this allows a reduction of
##           Queries to the database. (boolean)
## Showplot: This dictates whether the plot is closed or not after running the function, this is here to manage command
##           line behaviour where open plot figures can cause issues with preventing code from continuing to run. whilst
##           allowing this to be set to false so that figures are shown in Notebook form.
## DataFrame: Allows the use of a preprepared dataframe to use in the plots as well as prevents too many queries 
##            on the database
## PlanetsOnPlot: This dictates whether the circular approximation of planetary orbits is plotted on the figures.
## Filters: This is a parameter that should either be left as None to plot all filters on a single graph, or as
##          as a string that contains the names of each of the filters you want plotted, for example:
##          'grizy', 'y','rgy','zyri' are all valid inputs for filters.
def Heliocentric_BirdsEyeView(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,PlotPlanetsOnPlot,Filters]
    
    return BirdsEyeViewPlotter(*variables,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1)
  
 
## mindistance: Minimum Asteroid Distance from the sun you want in the plot (int) / au
## maxdistance: Maximum Asteroid Distance from the sun you want in the plot (int) / au
## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ally the user to explicitly specify the filename 
## DateInterval: This is how long you want to query about the date set above, -1 would be the 24 hours before the set date.
##               +1 would be 24 hours after set date (float), behaviour changed and now defaults to +1 date, this allows
##               this will allow you to alter the behaviour of the function and go forward or backword in time.
## KeepData: Used to keep query data in DataFrame Object that is returned from the function as this allows a reduction of
##           Queries to the database. (boolean)
## Showplot: This dictates whether the plot is closed or not after running the function, this is here to manage command
##           line behaviour where open plot figures can cause issues with preventing code from continuing to run. whilst
##           allowing this to be set to false so that figures are shown in Notebook form.
## DataFrame: Allows the use of a preprepared dataframe to use in the plots as well as prevents too many queries 
##            on the database
## PlanetsOnPlot: This is included for compatability with Birds eye view function, however, with topocentric this option is automatically not plotted (for obvious reasons)
## Filters: This is a parameter that should either be left as None to plot all filters on a single graph, or as
##          as a string that contains the names of each of the filters you want plotted, for example:
##          'grizy', 'y','rgy','zyri' are all valid inputs for filters.    
def Topocentric_BirdsEyeView(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None):
    
    variables =[mindistance,maxdistance,date,day,month,year,title,filename,
                DateInterval,KeepData,ShowPlot,DataFrame,PlotPlanetsOnPlot,Filters]
    
    return BirdsEyeViewPlotter(*variables,xyscale=['topocentricx','topocentricy','topocentric'],QueryNum=4)  

  
  

## mindistance: Minimum Asteroid Distance from the sun you want in the plot (int) / au
## maxdistance: Maximum Asteroid Distance from the sun you want in the plot (int) / au
## date: the date you want to query around (in median julian date) (defaults to current date.) (float)
## day   In regards to date, it will revert to the 24 hour window it is contained with
## month So 2023-08-04 [YYYY-MM-DD] would be the plot starting at 18:00 UTC (08-04) and end at 18:00 UTC (09-04)      
## year  and you can enter these as simply, days, months and year in UTC scale.   
## title: The Title you want the plot to have (str)
## filename : File name is used to ally the user to explicitly specify the filename 
## DateInterval: This is how long you want to query about the date set above, -1 would be the 24 hours before the set date.
##               +1 would be 24 hours after set date (float), behaviour changed and now defaults to +1 date, this allows
##               this will allow you to alter the behaviour of the function and go forward or backword in time.
## KeepData: Used to keep query data in DataFrame Object that is returned from the function as this allows a reduction of
##           Queries to the database. (boolean)
## Showplot: This dictates whether the plot is closed or not after running the function, this is here to manage command
##           line behaviour where open plot figures can cause issues with preventing code from continuing to run. whilst
##           allowing this to be set to false so that figures are shown in Notebook form.
## DataFrame: Allows the use of a preprepared dataframe to use in the plots as well as prevents too many queries 
##            on the database
## xyscale: The first two values in this list are your x and y values, and are entered as they appear in the database, the first value in the list if the appendage added to the
##          filename.
## xylabels: Allows custom labels for the x and y labels, passed as a list
## QueryNum: This refers to the Query Number as seen in Functions.Py that is being called by the function
## a_min,a_max: Are your minimum and maximum semi-major axis values that can be used to put a constraint on those values.
def iqeaBirdsEyeView(date=None,day=None,month=None,year=None,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,xyscale=['q','e','eccentricity-perhelion'],
                       xylabels=['perihelion (au)','eccentricity'],QueryNum=5,a_min=None,a_max=None):
    
    
    if(date is None) and (day is None or month is None or year is None):
        startdate, enddate, title = VariableTesting('','',Time.now().to_value('mjd', 'long'),day,month,year,title,1)
    else:
        QueryNum=6
        startdate, enddate, title = VariableTesting('','',date,day,month,year,title,DateInterval)

    
    # Here the program checks if there has been a DataFrame passed to the function, as if there is then it is used to reduce
    # the number of queries going to the database.
    # If the dataframe is not passed to the program then a Query is made to the database in the Queries function by using the DAL
    
    if(DataFrame is None):
        df = Queries(startdate,enddate,0,0,QueryNum,a_min,a_max)
        DataFrame = df.copy(deep=True)
    # The .copy(deep=True) is here to ensure immutability of the data contained, whilst it does force a second DF of 
    # equal size into memory it does allow the data to remain
    ## May need to write df = DataFrame and use copy to ensure the DataFrame that goes in is what comes out as as of right now
    ## This is not the case as df is returned not DataFrame
    else: df = DataFrame.copy(deep=True)    
    
    
    
    ## Replace this for all functions - Add Warning.
    if df.empty :
        print('No Results in this region for this timeframe')
        return df
    
    arguments = dict(marker='.',edgecolor=None )
    
    setplotlabelsandlimits = dict(xlim=[df[xyscale[0]].min(),df[xyscale[0]].max()],ylim=[df[xyscale[1]].min(),df[xyscale[1]].max()],xlabel=xylabels[0],ylabel=xylabels[1])
    

    #Creates the figure with a set size fixed at (10,10)
    plt.figure(figsize=(10,10))
    plot = sns.scatterplot(x=df[xyscale[0]],y=df[xyscale[1]],**arguments)
    #Labels the axes so that the user knows
    plot.set(**setplotlabelsandlimits)
    if(date is None) and (day is None or month is None or year is None):
        plt.suptitle(title,horizontalalignment='center')
    else:
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''),horizontalalignment='center')


    
    if (filename is not None):
        SavePlot(filename ,dict(),ShowPlot)
    elif title is not None:
        SavePlot(title+'-'+xyscale[2]+'-iqeabev' ,dict(),ShowPlot)


    if (KeepData == True):
        return DataFrame



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
         
