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
import warnings
warnings.filterwarnings(
    action='ignore', module='matplotlib.figure', category=UserWarning,
    message=('This figure includes Axes that are not compatible with tight_layout, '
             'so results might be incorrect.')
)
#Imports Package that contains the SQL interface
from DAL import DataAccessLayer as dal

def SavePlot(filename,extraargs,ShowPlot=False):
    #tight layout here is used to prevent elements of a plot from overlapping, ie axes, labels, titles etc
    #plt.tight_layout()
    #saves the figure, replaces whitespace with underscores, outputs as pdf and adds any extra arguements that get passed to the file
    # using an extraargs dictionary 
    plt.savefig(filename.replace(' ','_')+ '.pdf', format='pdf', bbox_inches='tight',**extraargs)
    #If the user doesn't want the plot shoown this should evaluate whether the parameter is true or false and then close the plot if
    # necessary.
    if ShowPlot == False:
        plt.close()
        
def PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance,axes=None):
    # For ensures sun and planets are only plotted for heliocentric plots. by checking against the query used and if it is an 
    # acceptable query ie query number 1 then the suns and planets are plotted based on the Plot Planets function
    if QueryNum ==1:
        plt.plot([0], [0], '.', color='orange', ms=3)
        if PlotPlanetsOnPlot == True:
            PlotPlanets(mindistance, maxdistance,axes)

#This function checks a list array to see if any of the values are not None and if they are then it returns a "AND"
# so that it can be added to the "cmd" variable in order to build a sql query dynamically.
def check_next(pair):
    if (any(i is not None for i in pair)):
        return """\n\tAND\n"""
    return ''


def Queries(startdate=None, enddate=None, mindistance=None, maxdistance=None, Query=None, a_min=None, a_max=None,
            q_min=None, q_max=None, i_min=None,
            i_max=None, e_min=None, e_max=None):
    min_max_pair = [[q_min, q_max], [i_min, i_max], [e_min, e_max], [a_min, a_max], [startdate, enddate]]
    params = {"startdate": startdate, "enddate": enddate, "mindistance": mindistance,
              "maxdistance": maxdistance, 'a_min': a_min, 'a_max': a_max, 'q_min': q_min, 'q_max': q_max
        , 'i_min': i_min,
              'i_max': i_max, 'e_min': e_min, 'e_max': e_max}
    if Query == 1:
        cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.midpointtai, diasources.mag,
               diasources.filter, sssources.heliocentricx,sssources.heliocentricy 
               FROM diasources,sssources WHERE 
               (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) 
               AND 
               (sssources.heliocentricdist > %(mindistance)s AND sssources.heliocentricdist < %(maxdistance)s) 
               AND 
               (diasources.diasourceid=sssources.diasourceid)"""
    elif Query == 2:
        cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.mag,
               diasources.filter, sssources.heliocentricdist, sssources.topocentricdist,
               sssources.eclipticbeta FROM
               diasources,sssources
               WHERE
               (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) AND
               (sssources.heliocentricdist > %(mindistance)s AND sssources.heliocentricdist < %(maxdistance)s) AND
               (diasources.diasourceid=sssources.diasourceid)
               """
    elif Query == 3:
        cmd = """SELECT COUNT(DISTINCT diasources.ssobjectid)
               FROM
               diasources,sssources
               WHERE
               midpointtai BETWEEN %(startdate)s AND %(enddate)s
               AND
               sssources.heliocentricdist BETWEEN %(mindistance)s AND %(maxdistance)s
               AND
               (diasources.diasourceid=sssources.diasourceid)
            """

    elif Query == 4:
        cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.midpointtai, diasources.mag,
               diasources.filter, sssources.topocentricx,sssources.topocentricy 
               FROM diasources,sssources WHERE (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) 
               AND 
               (sssources.topocentricdist > %(mindistance)s AND sssources.topocentricdist < %(maxdistance)s) 
               AND 
               (diasources.diasourceid=sssources.diasourceid)"""
    elif Query == 5:
        cmd = """SELECT mpcdesignation, ssobjectid, q,e,incl,mpch
               FROM MPCORB 
               WHERE
               (e <1) 
               AND 
               (q/(1-e) BETWEEN %(a_min)s AND %(a_max)s)"""
        df = dal.create_connection_and_queryDB(cmd, params)
        df['a'] = df["q"] / (1 - df["e"])
        return df
    elif Query == 6:
        cmd="""select Query.mpcdesignation, Query.ssobjectid, diaSources.diaSourceid, Query.q,Query.e,Query.incl,Query.mpch, diaSources.midPointTai,a
            from  (
        select MPCORB.mpcdesignation, MPCORB.ssobjectid, q,e,incl,mpch,q/(1-e) as a
            from MPCORB where 
            (e < 1)
         AND (q/(1-e) BETWEEN %(a_min)s AND %(a_max)s) 
        ) as Query
        
        JOIN diaSources USING (ssobjectid)
        JOIN ssSources USING (diaSourceid)
        WHERE (diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s)
        """
        df = dal.create_connection_and_queryDB(cmd, params)
        #df['a'] = df["q"] / (1 - df["e"])
        return df
    elif Query == 7:
        # max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
        count=0
        cmd = """SELECT MPCORB.mpcdesignation, MPCORB.ssobjectid, diaSources.diaSourceid, q,e,incl,mpch, diaSources.midPointTai
        FROM MPCORB 
        JOIN diaSources USING (ssobjectid)
        JOIN ssSources USING (diaSourceid)
        """
        if (any(i is not None for i in [a_min, a_max, q_min, q_max, i_min, i_max, e_min, e_max])):
            cmd += """\nWHERE\n"""
        count+=1
        if (q_min is not None and q_max is not None):
            cmd += """\t(q BETWEEN %(q_min)s AND %(q_max)s)"""
            check=cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (q_min is not None and q_max is None):
            cmd += """\t(q > %(q_min)s )"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (q_min is None and q_max is not None):
            cmd += """\t(q < %(q_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        count+=1
        if (i_min is not None and i_max is not None):
            cmd += """\t(incl BETWEEN %(i_min)s AND %(i_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (i_min is not None and i_max is None):
            cmd += """\t(incl > %(i_min)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (i_min is None and i_max is not None):
            cmd += """\t(incl < %(i_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        count+=1
        if (e_min is not None and e_max is not None):
            cmd += """\t(e BETWEEN %(e_min)s AND %(e_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (e_min is not None and e_max is None):
            cmd += """\t(e > %(e_min)s )"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (e_min is None and e_max is not None):
            cmd += """\t(e < %(e_max)s )"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        if (e_min is not None and e_min >= 1): a_min, a_max = None, None
        count+=1
        if (a_min is not None and a_max is not None):
            cmd += """\t(q/(1-e) BETWEEN %(a_min)s AND %(a_max)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is not None and a_max is None):
            cmd += """\t(q/(1-e) > %(a_min)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is None and a_max is not None):
            cmd += """\t(q/(1-e) < %(a_max)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        count+=1
        #         if ( tp_min  is not None and tp_max is not None):
        #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
        #         elif tp_min  is not None and tp_max is None):
        #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
        #         elif (tp_min  is None and tp_max is not None):
        #             """\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
        if (startdate is not None and enddate is not None):
            cmd += """\tdiaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                print(pair,check!=cmd)
                if check != cmd:
                    break
        elif (startdate is not None and enddate is None):
            cmd += """\tdiaSources.midPointTai > %(startdate)s"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (startdate is None and enddate is not None):
            cmd += """\tdiaSources.midPointTai < %(enddate)s"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        df = dal.create_connection_and_queryDB(cmd, params)
        if e_max is not None and e_max < 1:
            df['a'] = df['q'] / (1 - df['e'])
        return df
    elif Query == 8:
        min_max_pair = [[q_min, q_max], [i_min, i_max], [e_min, e_max], [a_min, a_max]]
        # max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
        count=0
        cmd = """SELECT MPCORB.mpcdesignation, MPCORB.ssobjectid, q,e,incl,mpch
        FROM MPCORB 
        """
        if (any(i is not None for i in [a_min, a_max, q_min, q_max, i_min, i_max, e_min, e_max])):
            cmd += """\nWHERE\n"""
        count+=1
        if (q_min is not None and q_max is not None):
            cmd += """\t(q BETWEEN %(q_min)s AND %(q_max)s)"""
            check=cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (q_min is not None and q_max is None):
            cmd += """\t(q > %(q_min)s )"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (q_min is None and q_max is not None):
            cmd += """\t(q < %(q_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        count+=1
        if (i_min is not None and i_max is not None):
            cmd += """\t(incl BETWEEN %(i_min)s AND %(i_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (i_min is not None and i_max is None):
            cmd += """\t(incl > %(i_min)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (i_min is None and i_max is not None):
            cmd += """\t(incl < %(i_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        count+=1
        if (e_min is not None and e_max is not None):
            cmd += """\t(e BETWEEN %(e_min)s AND %(e_max)s)"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (e_min is not None and e_max is None):
            cmd += """\t(e > %(e_min)s )"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (e_min is None and e_max is not None):
            cmd += """\t(e < %(e_max)s )"""
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        if (e_min is not None and e_min >= 1): a_min, a_max = None, None
        count+=1
        if (a_min is not None and a_max is not None):
            cmd += """\t(q/(1-e) BETWEEN %(a_min)s AND %(a_max)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is not None and a_max is None):
            cmd += """\t(q/(1-e) > %(a_min)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is None and a_max is not None):
            cmd += """\t(q/(1-e) < %(a_max)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        count+=1
        #         if ( tp_min  is not None and tp_max is not None):
        #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
        #         elif tp_min  is not None and tp_max is None):
        #             cmd+="""\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
        #         elif (tp_min  is None and tp_max is not None):
        #             """\n\tAND diaSources.midPointTai BETWEEN %(startdate)s AND %(enddate)s"""
        df = dal.create_connection_and_queryDB(cmd, params)
        if e_max is not None and e_max < 1:
            df['a'] = df['q'] / (1 - df['e'])
        return df
    else:
        print('No Query Called')
        return

    df = dal.create_connection_and_queryDB(cmd, params)

    return df

## PlotPlanets Function is used to plot relavent planets onto the generated plots
## mindistance: Minimum Asteroid Distance from the sun you want in the plot (int) / au
## maxdistance: Maximum Asteroid Distance from the sun you want in the plot (int) / au
## Notably PlotPlanets is likely to be a internal function for most plots and will not require user input.
def PlotPlanets(mindistance,maxdistance,axes=None):
    #Checks that min and max distance can be cast a floating point numbers.
    try:
        mindistance = float(mindistance) 
        maxdistance = float(maxdistance)
    except Exception as ex:
        # If Min/Max distance cannot be cast as floating point numbers than it prints an error message to console 
        print('Error in Min/Max Distance')
    # This line grabs the most recently used axis so that the planets can be plotted onto that axis 
    ax = plt.gca()
    # This is an array of the semi major axis distances of each of the planets 
    # as this in this we assume the orbits approximate to circular and as such take a to be the radius of said circle 
    planets = np.array([0.387,0.723,1,1.524,5.203,9.540,19.18,30.06])
    # For loop to check each planet in the array
    for orbits in planets:
        #Here we check if each planet is within the confines of the plot and of the query
        # as if the planet is outside that limit then it gives no info to the plot as it 
        # will not be shown to the user anyway.
        if (orbits <= maxdistance and orbits >= mindistance):
            # Here You check if the axes passed to the function is none as if it isn't then it will be 
            # used to plot onto, the behaviour at the moment assumes the plot is a jointgrid as the 
            # Marginals are problematic when using plt.gca() as they become the final axis or a colourbar could also be too
            # If no axis are passed then it should be fine to just add another patch to the plot in the form of a circle.
            if axes is not None:
                circle = plt.Circle((0, 0),orbits,color='black',fill=False)
                
                axes.ax_joint.add_patch(circle)
            else:
                ax.add_patch(plt.Circle(
                             (0, 0),
                             orbits,
                             color='black',
                             fill=False)
                             )

## DateorMJD - A function that can convert between a time format and MJD and back, the output type will be isot for going
## from MJD to a Day,Month,Year time.
## Day: The day of the month that is being entered - no leading zeros. (int/str)
## Month: The month of the year that is being entered - no leading zeros. (int/str)
## Year: The year that is being entered, must be 4 Digit (int/str)
## MJD: The Modified Julian Date you want converted back to UTC iso time. must be left empty if want to convert from UTC
##      to MJD (float)
def DateorMJD(Day=None,Month=None,Year=None,MJD=None,ConvertToIso=True):
    # Checks if the date is given in MJD or not
    if(MJD == None):
        #As date is not given as mjd then the Day,Month and Year are checked to see if they contain not None value 
        if(Day != None and Month != None and Year != None):
            #this line parses the date into a full take with  '-' in order to comply with iso format
            fulldate = str(Year)+'-'+str(Month)+'-'+str(Day)
            #returns the date as a AstroPy time object in iso format.
            return Time(fulldate)
        else: 
            #If both MJD and the Day,Month and Year provided are not satifactory then the function defaults to returning the current time
            # as a AstroPy time object.
            return Time.now()
    else:
        #Here we check if the ConvertToIso is true indicating that the user wants the time in the in iso format, which returns a string
        # of iso format, otherwise the function will return a AstroPy time object in the mjd format.
        if ConvertToIso:
            return Time(str(MJD),format='mjd').to_value('iso')
        else:
            return Time(str(MJD),format='mjd')

# Is used to decide the padding on limits for some of the plots with non user set bounds as such require dynamic padding
def DecideLimits(value):
    # This is used to make padding easier by flipping for negative and positive values to allow more padding to dynamically allow
    # both negative minimums, maximums or one of either whilst still ensuring proper padding around the extremes of the plot.
    if value <= 0:
            return (1.08)*value
    else:
        return (0.92)*value

#This is code repeated multiple times in the box/boxen plots as they each need to be padded it takes in 
## DoubleBox_en_Call
## ax : axes being plotted on at that time, as if there are both box and boxen plots then there will be more than one axes so
##      so it is useful to pass in the axis and it is easy to add limits and labels to the plot
## df : dataframe being used in the plot, may not be the most efficient way of doing this, however it is passed to this function
##      so that it can used to get min and maxes using col in order to set limits.
## col: used alongside df in order to set y limits.
## i, labels and units : i in an index for the labels and units arrays that are used to set the ylabels for each plot.
def DoubleBox_en_Call(ax,df,i, col,labels,units):
        ymin = DecideLimits(df[col].min())
        ymax = -1*DecideLimits(-1*df[col].max())
        ax.set_ylim(ymin, ymax)
        ax.set_ylabel(labels[i]+' '+units[i])
        ax.set_xlabel('Filter')        

        
# Used to generate start and endate and verify the ability to cast the title as a string.
# Still requires mindistance,maxdistance as part of legacy code, could be removed if removed in functions dependant on Variable testing
def VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval):
    try:
        #the start date is put into a holder, rounded down to the start of the date that is entered and then
        # the set is set to 2pm chile time as it will not be night time there and not a viable survey time.
        
        holderdate = mth.floor(DateorMJD(day,month,year,date,False).to_value('mjd', 'long'))+0.75           
        # Now in the case that the date interval is negative then the start date will be after the enddate, aleast traditonally,
        # as such if the date interval is positive then the startdate is set to the holder date and the end date is just the holder
        # + whatever user defined interval is added
        # Howevr if the date interval is negative then the + DateInterval will also be negative so you get the holder date + the date 
        # interval to be the start date as that will be a lower value than the holder date and as such will be sent to the queries function 
        # correctly 
        if(DateInterval>=0):
            startdate = holderdate
            enddate   = holderdate+ DateInterval
        else:
            startdate = holderdate + DateInterval
            enddate   = holderdate
        # Catches strange issues where the title may not be a string and not castable as a string and therefore shuts down the program.
        title = str(title)
    except Exception as ex:
        # If anything goes round whilst this check and dates calculation is undertake then then the program will execute a system exit.
        print('Error message: '+ex)
        return sys.exit()
    #this function then returns the correctly set startdates, endates and (title in string form.)
    return startdate,enddate,title

# Specific colourmap for 5 of the 6 filters, an extra colour may be required for the u filter, but that is not known yet.
coloruse = {'g':'#FF00FF','r':'#FF0000','i':'#0077BB','z':'#B22222','y':'#FFA500'}
#grizy

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
                        title='NaN',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
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
    
    
    
    
    if df.empty :
        warnings.warn('No Results in this region for this timeframe')
        return df
    
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
        plt.title(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))))
        
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
                currentfilter = df[df['filter']==filter[0]]
                #Creates the figure with a set size fixed at (10,10)
                plt.figure(figsize=(10, 10))
                plot=sns.scatterplot(x=currentfilter[xyscale[0]],y=currentfilter[xyscale[1]],**arguments)
                #Labels the axes so that the user knows
                plot.set(**setplotlabelsandlimits)
                plt.title(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate)))) 
                PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance)
                
                ax=plt.gca()
                lgd = ax.legend(loc='upper left', bbox_to_anchor=(1,1), borderpad = 2, )
                if (filename is not None):
                    SavePlot(filename +'-'+filter[0] ,dict(bbox_extra_artists=(lgd,)),ShowPlot)
                elif title is not None:
                    SavePlot(title +'-'+filter[0]+'-'+xyscale[2]+'-bev',dict(bbox_extra_artists=(lgd,)),ShowPlot)
                
        if (KeepData == True):
            return DataFrame
    


## HistogramPlot2D: This is a 2D Histogram density plot
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

def HistogramPlot2D(mindistance,maxdistance,date=None,day=None,month=None,year=None,
                        title='NaN',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,PlotPlanetsOnPlot = True,Filters=None,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1):

    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
 

    # This calls the function that interfaces with the DB and passes the query to the package that handles the connection
    # As the port interfaced only allows select queries no checks for SQL injection undertaken.- No confidential info contained anyway.
    if(DataFrame is None):
        df = Queries(startdate,enddate,mindistance,maxdistance,QueryNum)
        DataFrame = df.copy(deep=True)
    else: df = DataFrame.copy(deep=True)    
    
    
    arguments = dict(marginal_ticks=True, xlim =[-maxdistance,maxdistance], ylim =[-maxdistance,maxdistance], 
                        kind="hist", cbar=True, cbar_kws=dict(shrink=0.75, use_gridspec=False),
                        binwidth= 0.04*maxdistance,edgecolor = 'none')
    jointplotarguments = dict(edgecolor = 'none',binwidth=0.04*maxdistance)
    
    if df.empty :
        warnings.warn('No Results in this region for this timeframe')
        return df
    
    if Filters is None:
        sns.set_theme(style="ticks")
        m=sns.jointplot( x=df[xyscale[0]], y=df[xyscale[1]], color='#0077BB', **arguments)
        m.plot_joint(sns.histplot,**jointplotarguments)
        
        # get the current positions of the joint ax and the ax for the marginal x
        pos_joint_ax = m.ax_joint.get_position()
        pos_marg_x_ax = m.ax_marg_x.get_position()
        ## reposition the joint ax so it has the same width as the marginal x ax
        m.ax_joint.set_position([pos_joint_ax.x0, pos_joint_ax.y0, pos_marg_x_ax.width, pos_joint_ax.height])
        # reposition the colorbar using new x positions and y positions of the joint ax
        m.fig.axes[-1].set_position([1, pos_joint_ax.y0+0.1, 0.1, 0.8*pos_joint_ax.height])       
        m.set_axis_labels('x (au)', 'y (au)')
        
        
        ##
        
        
        #common to all plots
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')
        #plt.tight_layout()
        PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance,m)
        if (filename is not None):
            SavePlot(filename ,dict(),ShowPlot)
        else:
            SavePlot(title +'-'+xyscale[2]+'-2DHist',dict(),ShowPlot)
 
        if (KeepData == True):
            return DataFrame
    else:
        filters = df['filter'].groupby(df['filter']).unique()
        for filter in filters:
            if re.search(filter[0],Filters):
                currentfilter = df[df['filter']==filter[0]]
                sns.set_theme(style="ticks")
                m=sns.jointplot( x=currentfilter[xyscale[0]],y=currentfilter[xyscale[1]],color=coloruse[filter[0]],
                                **arguments)
                m.plot_joint(sns.histplot,color=coloruse[filter[0]],**jointplotarguments)
                plt.suptitle(title+' '+filter[0]+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')
                #plt.tight_layout()
                PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance,m)
                
                # get the current positions of the joint ax and the ax for the marginal x
                pos_joint_ax = m.ax_joint.get_position()
                pos_marg_x_ax = m.ax_marg_x.get_position()
                ## reposition the joint ax so it has the same width as the marginal x ax
                m.ax_joint.set_position([pos_joint_ax.x0, pos_joint_ax.y0, pos_marg_x_ax.width, pos_joint_ax.height])
                # reposition the colorbar using new x positions and y positions of the joint ax
                m.fig.axes[-1].set_position([1, pos_joint_ax.y0+0.1, 0.1, 0.8*pos_joint_ax.height])
                m.set_axis_labels('x (au)', 'y (au)')
    
                if (filename is not None):
                   SavePlot(filename+filter[0] ,dict(),ShowPlot)
                else:
                   SavePlot(title +'-'+filter[0]+'-'+xyscale[2]+'-2DHist' ,dict(),ShowPlot)
                
        if (KeepData == True):
            return DataFrame
    

  
## HexPlot: This is a 2D density plot with hexagonal bins instead of 
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
def HexPlot(mindistance,maxdistance,date=None,day=None,month=None,year=None,
            title='NaN',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
            DataFrame=None,GridSize=40,PlotPlanetsOnPlot=True,Filters=None,xyscale=['heliocentricx','heliocentricy','heliocentric'],QueryNum=1):

    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
    
    
    arguments = dict(kind = "hex", xlim =[-maxdistance,maxdistance],ylim =[-maxdistance,maxdistance], gridsize=GridSize,
                     extent = [-maxdistance,maxdistance,-maxdistance,maxdistance], edgecolors='none')
    
    
    if DataFrame is None:
        df = Queries(startdate,enddate,mindistance,maxdistance,QueryNum)
        DataFrame = df.copy(deep=True)
    else:
        df = DataFrame.copy(deep=True)
        
        
    if df.empty :
        warnings.warn('No Results in this region for this timeframe')
        return df
    
    if Filters is None :
        sns.set_theme(style="ticks")
        
        hexplot = sns.jointplot(x=df[xyscale[0]], y=df[xyscale[1]],
                                #color="#4CB391",
                                **arguments)
        plttitle = plt.suptitle(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')
        
        PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance,hexplot)
        # make new ax object for the cbar
        cbar_ax = hexplot.fig.add_axes([1, .25, .025, .4])  # x, y, width, height
        plt.colorbar(cax=cbar_ax)
        hexplot.set_axis_labels('x (au)', 'y (au)')
        
        if (filename is not None):
            SavePlot(filename, dict(),ShowPlot)
        else:
            SavePlot(title+'-'+xyscale[2]+'-hexbin' ,dict(),ShowPlot)
              
        
        if (KeepData == True):
            return DataFrame
    else:
        filters = df['filter'].groupby(df['filter']).unique()
        for filter in filters:
            if re.search(filter[0],Filters):
                currentfilter = df[df['filter']==filter[0]]
                sns.set_theme(style="ticks")
                hexplot = sns.jointplot(x=currentfilter[xyscale[0]],y=currentfilter[xyscale[1]],
                                        color = coloruse[filter[0]],**arguments )
                plt.suptitle(title+' Filter: '+filter[0]+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')
                
                PlotSunandPlanets(QueryNum,PlotPlanetsOnPlot,mindistance, maxdistance,hexplot)
                    
                cbar_ax = hexplot.fig.add_axes([1, .25, .025, .4])  # x, y, width, height
                plt.colorbar(cax=cbar_ax)
                hexplot.set_axis_labels('x (au)', 'y (au)')
                
                if (filename is not None):
                   SavePlot(filename+filter[0] ,dict(),ShowPlot)
                else:
                   SavePlot(title +'-'+filter[0]+'-'+xyscale[2]+'-hexbin' ,dict(),ShowPlot)
                                                                                    
        if (KeepData == True):
            return DataFrame


        
def HelioDistHist(date=None,day=None,month=None,year=None,title='', 
                  filename=None,DateInterval = 7 ,KeepData=False,ShowPlot=True,
                  DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]],LogY=True):
    
   
    
    startdate, enddate, title = VariableTesting(0,0,date,day,month,year,title,DateInterval)
    dates = np.linspace(0,DateInterval-1,DateInterval)
    counters = np.ndarray((len(dates)*len(DistanceMinMax),3))
    ticks = np.ndarray.tolist(np.linspace(0,DateInterval,DateInterval+1)-0.5)
       


    if DateInterval > 7:
        OutputDF=ps.DataFrame()
        i=0
        while i < (DateInterval // 7):
            if filename is not None: 
                filename += '-'+str(i+1)
            if KeepData:
                OutputDF = ps.concat([OutputDF,HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename,7,
                          KeepData,ShowPlot,DistanceMinMax,LogY)])
            else:
                HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename,7,
                          KeepData,ShowPlot,DistanceMinMax,LogY)
            i+=1
        if (DateInterval % 7) !=0:
            if KeepData:
                OutputDF = ps.concat([OutputDF,HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename,(DateInterval % 7),
                          KeepData,ShowPlot,DistanceMinMax,LogY)])
                    
            else:
                HelioDistHist(startdate+i*7,day,month,year,title+' Plot #'+str(i+1), filename,(DateInterval % 7),
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
        
    
    ax.set_xticks(ticks)
    ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in dates+startdate]
    ax.set_xticklabels(ProperDateLabels+[DateorMJD(MJD=enddate,ConvertToIso=False).to_value(format='iso',subfmt='date')],horizontalalignment='left',rotation=-40)
    ax.set(yscale="log")
    if (filename is not None):
        SavePlot(filename, dict(),ShowPlot)
    else:
        SavePlot(title+'-heliodisthist' ,dict(),ShowPlot)
    if (KeepData == True):
        return NewData        

        
def MonthlyHelioDistHist(date=None,day=None,month=None,year=None,title='', 
                         filename=None,DateInterval = 8 ,KeepData=False,ShowPlot=True,
                         DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]]):
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
        print(startdate,enddate)
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
            ax.set(yscale="log")
            i+=1
    else:
        ax = sns.barplot(data=NewData,x='Date',y='Detections',hue='distance')
        ax.set_xticks(ticks)
        ax.set_xticklabels(Dates[0:7])
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
                         DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]]):

    date = DateorMJD(MJD=date,Day=day,Month=month,Year=year,ConvertToIso=False).to_value(format='iso',subfmt='date').split('-')
    #date[0] = str(int(date[0])+1)
    #date[-1] = '01'
    #date[-2] = '01'
    #date





    counters = np.ndarray((DateInterval*len(DistanceMinMax),3))

    ticks = np.ndarray.tolist(np.linspace(0,DateInterval-1,DateInterval))
    count=0
    Dates = []
    for i in range(0,DateInterval):

        startdate =Time('-'.join(date)).to_value('mjd')
        Dates+=[DateorMJD(MJD=startdate,ConvertToIso=False).to_value(format='iso',subfmt='date')]
        date[0] = str(int(date[0])+1)
        enddate =Time('-'.join(date)).to_value('mjd')
        print(startdate,enddate)
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
            ax.set(yscale="log")
            i+=1
    else:
        legend = ["{:.2f}".format(round(distance[2],2))+'-'+"{:.2f}".format(round(distance[3],2))+' (au)' for i,distance in enumerate(distances)]
        ax =sns.barplot(x=NewData['Date'],y=NewData['Detections'],hue=NewData['distance'],)
        ax.set_xticks(ticks)
        ax.set_xticklabels(Dates)
        ax.legend(handles=ax.legend_.legendHandles, labels=legend,loc='upper left', bbox_to_anchor=(1,1), borderpad = 2,)
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
    
    ax = sns.barplot(x=counters[0,:],y=counters[1,:],color='#FF00FF')
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
        
        
def boxwhisker_plot(mindistance,maxdistance,date=None,day=None,month=None,year=None,boxOrBoxen=2,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,Filters=None):
    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
    if DataFrame is None:
        df = Queries(startdate,enddate,mindistance,maxdistance,2)
        DataFrame = df.copy(deep=True)
    else:
        df = DataFrame.copy(deep=True)
    extension = ''   
    sorter = ['g','r','i','z','y']
    sorterIndex = dict(zip(sorter, range(len(sorter))))    
    selection = ['mag', 'heliocentricdist','topocentricdist', 'eclipticbeta']
    units = ['H','(au)','(au)','(Degrees)']
    labels = ['Absolute Magnitude','Heliocentic Distance','Topocentric Distance', 'Ecliptic Beta Angle']
    df['numeric'] = df['filter'].map(sorterIndex)
    
    if Filters is not None:
        if Filters != 'ALL':
            extension = '-'+Filters
            check = ps.DataFrame()
            for booleanIndex in [df['filter'] == letter for letter in Filters]:
                check = ps.concat([check,df[booleanIndex]])
            df=check
        else:
            df['filter'] = 'All'
            extension = '-ALL'
            
    additiontoextension = {0:'-box',1:'-boxen',2:'-box-and-boxen'}
    extension+=additiontoextension[boxOrBoxen]
    if maxdistance >= 10:
        selection.pop(2)
        units.pop(2)
        labels.pop(2)
    if boxOrBoxen == 2 :
        fig, axes = plt.subplots(2, len(selection),figsize=(10*len(selection),20))
    else:
        fig, axes = plt.subplots(1, len(selection),figsize=(10*len(selection),10))
    for i, col in enumerate(selection):
        sns.color_palette('colorblind')
        if boxOrBoxen == 0:
            ax = sns.boxplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
        elif boxOrBoxen == 1:
            ax = sns.boxenplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
        elif boxOrBoxen == 2:
            ax = sns.boxplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
            ax = sns.boxenplot(x=df.sort_values(by='numeric')['filter'],y=df[col], ax=axes.flatten()[len(selection)+i])
            DoubleBox_en_Call(ax,df,i, col,labels,units)
    
    plt.suptitle(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),size= 'xx-large',horizontalalignment='center')
    if filename is None:
        SavePlot(title+extension,dict(),ShowPlot=ShowPlot)
    else: 
        SavePlot(filename,dict(),ShowPlot=ShowPlot)
    if (KeepData == True):
        return DataFrame
    
    
    
def violin_plot(mindistance,maxdistance,date=None,day=None,month=None,year=None,boxOrBoxen=2,
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                        DataFrame=None,Filters=None):
    startdate, enddate, title = VariableTesting(mindistance,maxdistance,date,day,month,year,title,DateInterval)
    if DataFrame is None:
        df = Queries(startdate,enddate,mindistance,maxdistance,2)
        DataFrame = df.copy(deep=True)
    else:
        df = DataFrame.copy(deep=True)
        
    sorter = ['g','r','i','z','y']
    sorterIndex = dict(zip(sorter, range(len(sorter))))    
    selection = ['mag', 'heliocentricdist','topocentricdist', 'eclipticbeta']
    units = ['H','(au)','(au)','(Degrees)']
    labels = ['Absolute Magnitude','Heliocentic Distance','Topocentric Distance', 'Ecliptic Beta Angle']
    df['numeric'] = df['filter'].map(sorterIndex)
    
    if Filters is not None:
        if Filters != 'ALL':
            check = ps.DataFrame()
            for booleanIndex in [df['filter'] == letter for letter in Filters]:
                check = ps.concat([check,df[booleanIndex]])
            df=check
        else:
            df['filter'] = 'All'
            
    
    
    if maxdistance >= 10:
        selection.pop(2)
        units.pop(2)
        labels.pop(2)
    fig, axes = plt.subplots(1, len(selection),figsize=(10*len(selection),10))
    for i, col in enumerate(selection):
        sns.color_palette('colorblind')
        ax = sns.violinplot(x=df.sort_values(by='numeric')['filter'],y=df[col],
                            bw=0.1,

                            ax=axes.flatten()[i])
        DoubleBox_en_Call(ax,df,i, col,labels,units)
    
    plt.suptitle(title)
    plt.tight_layout()
    if (filename is not None):
        SavePlot(filename, dict(),ShowPlot)
    else:
        SavePlot(title+'-violin' ,dict(),ShowPlot)
    if (KeepData == True):
        return df   

    
    
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
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')


    
    if (filename is not None):
        SavePlot(filename ,dict(),ShowPlot)
    elif title is not None:
        SavePlot(title+'-'+xyscale[2]+'-iqeabev' ,dict(),ShowPlot)


    if (KeepData == True):
        return DataFrame

# theframe = iqeaBirdsEyeView(60042,a_min=27,a_max=80,KeepData=True)
# iqeaBirdsEyeView(60042,a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',])
# iqeaBirdsEyeView(60042,a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity'])
# iqeaBirdsEyeView(60042,a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','incl','inclination-semimajor'],xylabels=['semimajor axis (au)','inclination (degrees)'])

# theframe = iqeaBirdsEyeView(a_min=27,a_max=80,KeepData=True)
# iqeaBirdsEyeView(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',])
# iqeaBirdsEyeView(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity'])
# iqeaBirdsEyeView(a_min=27,a_max=80,KeepData=True,DataFrame=theframe,xyscale=['a','incl','inclination-semimajor'],xylabels=['semimajor axis (au)','inclination (degrees)'])  


# iqe

# i q

# i e

# q e

 
    
def iqeaHistogramPlot2D(date=None,day=None,month=None,year=None,
                       title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                       DataFrame=None,xyscale=['q','e','eccentricity-perhelion'],
                       xylabels=['perihelion (au)','eccentricity'],a_min=None,a_max=None,QueryNum=5):


    if(date is None) and (day is None or month is None or year is None):
        startdate, enddate, title = VariableTesting('','',Time.now().to_value('mjd', 'long'),day,month,year,title,1)
    else:
        QueryNum=6
        startdate, enddate, title = VariableTesting('','',date,day,month,year,title,DateInterval)

 

    # This calls the function that interfaces with the DB and passes the query to the package that handles the connection
    # As the port interfaced only allows select queries no checks for SQL injection undertaken.- No confidential info contained anyway.
    if(DataFrame is None):
        df = Queries(startdate,enddate,0,0,QueryNum,a_min,a_max)
        DataFrame = df.copy(deep=True)
    else: df = DataFrame.copy(deep=True)    
    
    
    arguments = dict(marginal_ticks=True, 
                        kind="hist", cbar=True, cbar_kws=dict(shrink=0.75, use_gridspec=False),
                        edgecolor = 'none')
    jointplotarguments = dict(edgecolor = 'none')
    
    if df.empty :
        return print('No Results in this region for this timeframe')
    
    
    sns.set_theme(style="ticks")
    m=sns.jointplot( x=df[xyscale[0]], y=df[xyscale[1]], color='#0077BB',binwidth=[abs(0.002*(df[xyscale[0]].max()-df[xyscale[0]].min())),abs(0.002*(df[xyscale[1]].max()-df[xyscale[1]].min()))], **arguments)
    m.plot_joint(sns.histplot,**jointplotarguments)
        
    # get the current positions of the joint ax and the ax for the marginal x
    pos_joint_ax = m.ax_joint.get_position()
    pos_marg_x_ax = m.ax_marg_x.get_position()
    ## reposition the joint ax so it has the same width as the marginal x ax
    m.ax_joint.set_position([pos_joint_ax.x0, pos_joint_ax.y0, pos_marg_x_ax.width, pos_joint_ax.height])
    # reposition the colorbar using new x positions and y positions of the joint ax
    m.fig.axes[-1].set_position([1, pos_joint_ax.y0+0.1, 0.1, 0.8*pos_joint_ax.height])       
    m.set_axis_labels(*xylabels)
        
    if(date is None) and (day is None or month is None or year is None):
        plt.suptitle(title,horizontalalignment='center')
    else:
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')

    if (filename is not None):
        SavePlot(filename ,dict(),ShowPlot)
    else:
        SavePlot(title +'-'+xyscale[2]+'-iqea2DHist',dict(),ShowPlot)
 
    if (KeepData == True):
        return DataFrame

  
## HexPlot: This is a 2D density plot with hexagonal bins instead of 
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

def iqeaHexPlot(date=None,day=None,month=None,year=None,title='',
                filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
                DataFrame=None,xyscale=['q','e','eccentricity-perhelion'],
                       xylabels=['perihelion (au)','eccentricity'],a_min=None,a_max=None,QueryNum=5,GridSize=40):
    if(date is None) and (day is None or month is None or year is None):
        startdate, enddate, title = VariableTesting('','',Time.now().to_value('mjd', 'long'),day,month,year,title,1)
    else:
        QueryNum=6
        startdate, enddate, title = VariableTesting('','',date,day,month,year,title,DateInterval)

    arguments = dict(kind = "hex", gridsize=GridSize, edgecolors='none')


    if DataFrame is None:
     df = Queries(startdate,enddate,0,0,QueryNum,a_min,a_max)
     DataFrame = df.copy(deep=True)
    else:
     df = DataFrame.copy(deep=True)


    if df.empty :
     return print('No Results in this region for this timeframe')


    sns.set_theme(style="ticks")

    hexplot = sns.jointplot(x=df[xyscale[0]], y=df[xyscale[1]],xlim=[df[xyscale[0]].min(),df[xyscale[0]].max()],
                         #color="#4CB391",
                         ylim=[df[xyscale[1]].min(),df[xyscale[1]].max()],
                         extent=[df[xyscale[0]].min(),df[xyscale[0]].max(),df[xyscale[1]].min(),df[xyscale[1]].max()],
                         **arguments)
    

    #hexplot.ax_joint(extent=[*axes.get_ylim(),*axes.get_xlim()])
    if(date is None) and (day is None or month is None or year is None):
        plt.suptitle(title,horizontalalignment='center')
    else:
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate))+' - '+str(DateorMJD(MJD=float(enddate))),horizontalalignment='center')

    


    # make new ax object for the cbar
    cbar_ax = hexplot.fig.add_axes([1, .25, .025, .4])  # x, y, width, height
    plt.colorbar(cax=cbar_ax)
    hexplot.set_axis_labels(*xylabels)

    if (filename is not None):
     SavePlot(filename, dict(),ShowPlot)
    else:
     SavePlot(title+'-'+xyscale[2]+'-hexbin' ,dict(),ShowPlot)


    if (KeepData == True):
     return DataFrame





