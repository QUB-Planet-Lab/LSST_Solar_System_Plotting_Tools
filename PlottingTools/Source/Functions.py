import pandas as ps
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math as mth
from astropy.time import Time
import re
import sys
import pytest
#Imports Package that contains the SQL interface
import DataAccessLayer as dal
sns.set_context(font_scale=1.4)
import warnings
warnings.filterwarnings(
    action='ignore', module='matplotlib.figure', category=UserWarning,
    message=('This figure includes Axes that are not compatible with tight_layout, '
             'so results might be incorrect.')
    
)





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


## This is the Queries Function that handles all connections to the Database.
## startdate: Start date of the Query window, only useful for Querys 1-4,6-7
## enddate: enddate date of the Query window, only useful for Querys 1-4,6-7
## mindistance,maxdistance: the min and maximum heliocentric or topocentric distance for Queries 1-4 
## Query: Denotes the Query being called and is a numerical variable between 1 and 8 inclusive.
## a_min: minimum semi major axis value acceptable within the query (au), only useful for Querys 5-8
## a_max: maximum semi major axis value acceptable within the query (au), only useful for Querys 5-8
## q_min: the perhelion value you want as the minimum in your Query (au), only useful for Querys 6-8
## q_max: the perhelion value you want as the maximum in your Query (au), only useful for Querys 6-8
## i_min: the inclination value (degrees) you want as minimum in your query, only useful for Querys 6-8
## i_max: the inclination value (degrees) you want as maximum in your query, only useful for Querys 6-8
## e_min: the eccentricity value you want as the minimum in your query, only useful for Querys 6-8 
## e_max: the eccentricity value you want as your maximum in your query, only useful for Querys 6-8
def Queries(startdate=None, enddate=None, mindistance=None, maxdistance=None, Query=None, a_min=None, a_max=None,
            q_min=None, q_max=None, i_min=None,
            i_max=None, e_min=None, e_max=None):
    #These are our parameters, they all get sent to the database with the query, but only the ones with %(EXAMPLE)s are used in each query
    params = {"startdate": startdate, "enddate": enddate, "mindistance": mindistance,
              "maxdistance": maxdistance, 'a_min': a_min, 'a_max': a_max, 'q_min': q_min, 'q_max': q_max
                ,'i_min': i_min,'i_max': i_max, 'e_min': e_min, 'e_max': e_max}
    #This if statement effectively works like a case switch statement with the Query parameter being checked against a number 
    if Query == 1:
        ## This is the command that goes to the database
        ## This is a query that gets the detection id, corresponding object id, the detection time, the magnitude of the detection
        ## the filter the detection was made in and the heliocentric x and y distance components.
        cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.midpointtai, diasources.mag,
               diasources.filter, sssources.heliocentricx,sssources.heliocentricy 
               FROM diasources,sssources WHERE 
               (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) 
               AND 
               (sssources.heliocentricdist > %(mindistance)s AND sssources.heliocentricdist < %(maxdistance)s) 
               AND 
               (diasources.diasourceid=sssources.diasourceid)"""
    elif Query == 2:
         ## This is the command that goes to the database
         ## This query grabs the detection id, the corresponding object id, the magnitude of detection, the filter, the heliocentric
         ## and topocentric distances and the ecliptic beta angle with user based constaints on start and enddate, heliocentric distance
         ## and the tables are joined on detection detection source id
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
        ## This is the command that goes to the database
        ## This counts the distinct ie unique object detections within a certain time period and heliocentric distance range.
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
        ## This is the command that goes to the database
        ## This is a query that gets the detection id, corresponding object id, the detection time, the magnitude of the detection
        ## the filter the detection was made in and the topocentric x and y distance components.
        ## with user set constaints on time range, and topocentric distance range.
        cmd = """SELECT diasources.diasourceid, diasources.ssobjectid,diasources.midpointtai, diasources.mag,
               diasources.filter, sssources.topocentricx,sssources.topocentricy 
               FROM diasources,sssources WHERE (midpointtai >  %(startdate)s) AND  (midpointtai <= %(enddate)s) 
               AND 
               (sssources.topocentricdist > %(mindistance)s AND sssources.topocentricdist < %(maxdistance)s) 
               AND 
               (diasources.diasourceid=sssources.diasourceid)"""
    elif Query == 5:
        ## Returns all bound objects with a semi major axis between the min and max semi major axis distance range, the information 
        ## returned includes the microplanetcenter designation, the object id in the database, the perihelion of the object, the 
        ## eccentricity, the inclination and the mpch (magnitude)
        cmd = """SELECT mpcdesignation, ssobjectid, q,e,incl,mpch
               FROM MPCORB 
               WHERE
               (e <1) 
               AND 
               (q/(1-e) BETWEEN %(a_min)s AND %(a_max)s)"""
        ## This gets the query and then adds an extra column with the semi major axis, as this is e<1 this could be implemented in 
        ## SQL instead by using (q/(1-e) as a) alternatively. and as 1-e will never be 0 then there will be no errors with respect to
        ## division by zero errors
        df = dal.create_connection_and_queryDB(cmd, params)
        df['a'] = df["q"] / (1 - df["e"])
        return df
    elif Query == 6:
        ## Returns all bound detections with a semi major axis between the min and max value distance range, and for a datetime range between the start and end date.
        ## The interformation returned includes the mpc designation, the object id and detection id aswell as the perihelion, eccentricty, mpch, detection time.
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
        ## calls the data access function in DataAccessLayer in order to contact the database. 
        df = dal.create_connection_and_queryDB(cmd, params)
        ## this returns the dataframe that contains the information from the query back to whatever function called the Queries function
        return df
    elif Query == 7:
        ## min_max_pair contains all the minmax pairs that are used on this queries and this allows each if,elif,elif function to 
        ## check whether any of the next sets of parameters is not None as this will allow an "AND" statement to be added to the SQL or ommitted if necessary.
        min_max_pair = [[q_min, q_max], [i_min, i_max], [e_min, e_max], [a_min, a_max], [startdate, enddate]]
        # max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
        ## Is used to slice the min_max_pair list when checking if one of the next parameters is constrained by the user.
        count=0
        ## Query returns in the MPC Designation, the object id, the detection id, the perihelion, semimajor axis, eccentricity, semi major axis which defaults to Null if 
        ## the eccentricity is 1, the query also returns the inclination, mpc H aswell as the detection time (ie the midpoint of the image esposure.)
        cmd = """SELECT MPCORB.mpcdesignation, MPCORB.ssobjectid, diaSources.diaSourceid, q,e,q/NULLIF(1-e,0) as a,incl,mpch, diaSources.midPointTai
        FROM MPCORB 
        JOIN diaSources USING (ssobjectid)
        JOIN ssSources USING (diaSourceid)
        """
        ## This if checks if there are any constaints at all.
        if (any(i is not None for i in [a_min, a_max, q_min, q_max, i_min, i_max, e_min, e_max,startdate, enddate])):
            cmd += """\nWHERE\n"""
        count+=1
        ## count is set to 1 here was you do not need to check the parameter that is initially added.
        ## This if,elseif and elseif set up allows you to allow for upper, lower or both bounds
        ## As I was commenting this it occurs it may be usefull to pull each if,elif,elif structure into a method call as that will allow the cut down on code and just use
        ## a for loop to work through this. 
        
        ## So these if,elif,elif statements just check if both the parameters are not None, ie both bounds are there,
        ## then checks if there is a lower bound on the parameter if both aren't bounded, and then if there is no lower bound, it checks if there is an upperbound. 
        if (q_min is not None and q_max is not None):
            ## This adds a inclusive upper and lower bound on q
            cmd += """\t(q BETWEEN %(q_min)s AND %(q_max)s)"""
            #Then we set check equal to the sql command string so that when the check_next function checks the next parameters that if an "AND" is added the check will no longer
            ## be equal to the cmd and therefore breaks out of the for loop as there is no need to check any more or you would risk multiple "AND" strings being added.
            check=cmd
            ## the min_max_pair that is the list of lists so [[0,0],[0,0]] etc is sliced using count to not check the current or past variables. 
            ## this for loop splits the list of lists into their pairs so [a_min,a_max] would be a possible pair.
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
        ## count is incremented by one in order to move the slice of min_max_pair for further checks using the check_next function
        ## The rest of these IF-ELIF-ELIF groups follow the same pattern so possibility of refactoring into a method in future to improve readability.
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
        ## count incremented again to move the slice further down the list.
        count+=1
        ## This is similar to the other IF-ELIF-ELIF in having the same structure however the addition to the cmd is slightly different
        ## in there is q/NULLIF(1-e,0) which is used to deal with a division by zero error and if e=1 ie the semi major axis is at infinity, so we use the null indicator to filter
        ## that out.
        if (a_min is not None and a_max is not None):
            cmd += """\t(q/NULLIF(1-e,0) BETWEEN %(a_min)s AND %(a_max)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is not None and a_max is None):
            cmd += """\t(q/NULLIF(1-e,0) > %(a_min)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is None and a_max is not None):
            cmd += """\t(q/NULLIF(1-e,0) < %(a_max)s) """
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
        ## This here is used to add the date constraints in the same way with checking if startdate and enddate are not None so both are bounded, if only startdate is set 
        ## so only a lower bound or only enddate is Not None so an upperbound.
        ## The interation to check next parameters works through min_max being sliced at the end, therefore there are no 'pair' in it so no "AND" statement is appended.
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
        ## This contacts the DataAccessLayer File by calling a function that initiates connection to the database, and then the parameters and the sql statement are handed to the
        ## database, and by using postgresql the parameters will be considered as variables only and will not accidentially be executed as SQL code,
        df = dal.create_connection_and_queryDB(cmd, params)
        
        ## No need for this as we handled adding the a table on the database side and handle any division by zero errors there too. 
        #df['a'] = df['q'] / (1 - df['e'])
        return df
    elif Query == 8:
        ## This query is pretty much similar to the previous query except it just has the exclusion of the time bounds which simply means it returns objects rather than detections
        min_max_pair = [[q_min, q_max], [i_min, i_max], [e_min, e_max], [a_min, a_max]]
        # max_a, min_a, q_min,q_max,i_min, i_max , e_min, e_max
        count=0
        ## Query returns in the MPC Designation, the object id the perihelion, semimajor axis, eccentricity, semi major axis which defaults to Null if 
        ## the eccentricity is 1, the query also returns the inclination and mpc H it allows user set constraints on e,a,q and i  
        cmd = """SELECT MPCORB.mpcdesignation, MPCORB.ssobjectid, q,e,q/NULLIF(1-e,0) as a,incl,mpch
        FROM MPCORB 
        """
        ## Checks that there are actually parameters that are not None in the following list 
        if (any(i is not None for i in [a_min, a_max, q_min, q_max, i_min, i_max, e_min, e_max])):
            cmd += """\nWHERE\n"""
        count+=1
        ## count is incremented in order to ^ slice the array after the [q_min,q_max] list item within the min_max_pair list
        ## Once again this checks if q_min and q_max are both Not None to check whether both are bounded so a lower perhelion and higher perihelion value
        ## if only q_min is set it adds a lower bound and if only q_max is set then it only adds an upper bound for q to the sql statement.
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
        ## count is incremented so the min_max_pair array is sliced correctly for the for statement when checking with check_next as we don't want to add an "AND" for parameters
        ## that have already been added to the statement.
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
            
        count+=1
        ## once again we use the NULLIF(1-e,0) to prevent division by zero when e is equal to 1 as at that point semi major axis tends to infinity. as it will replace the value
        ## with a SQL null value which also will be excluded with there is a min or max value for a. 
        if (a_min is not None and a_max is not None):
            cmd += """\t(q/NULLIF(1-e,0) BETWEEN %(a_min)s AND %(a_max)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is not None and a_max is None):
            cmd += """\t(q/NULLIF(1-e,0) > %(a_min)s) """
            check = cmd
            for pair in min_max_pair[count:]:
                cmd += check_next(pair)
                if check != cmd:
                    break
        elif (a_min is None and a_max is not None):
            cmd += """\t(q/NULLIF(1-e,0) < %(a_max)s) """
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
        ## contacts the database with the fully constructed sql command and passes it and the parameters to the database.
        df = dal.create_connection_and_queryDB(cmd, params)
    
        return df
    else:
        ## if the query number entered doesn't map to any of the queries then this is printed and a NoneType is returned.
        ## it may be useful to return an empty dataframe instead to prevent errors from being raised when this happens.
        print('No Query Called')
        return
    ## for the queries that do not immediately call the database the rest get pushed to the database with the parameters now and then return that dataframe to the function calling
    ## this Query function.
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
    ## sets ymin based on the minimum value in the dataframe column
    ## sets ymax based on the maximum value in the dataframe column passed to the function,
    ## DecideLimits is the function that is used to pad the y limits
        ymin = DecideLimits(df[col].min())
        ## for ymax we use -1* on the max so that when the value is evaluated it flips sign so that the negative and positive values are padded the same way
        ## and then we flip it back onces it comes out of the function, this allows us to cover eventualities where you have both negative min and max values on the y and 
        ## handle them in the same way.
        ymax = -1*DecideLimits(-1*df[col].max())
        ## we then set y limit using these newly padded values and we set the y label using the labels list and units list so ie heliocentric distance and (au)
        ax.set_ylim(ymin, ymax)
        ax.set_ylabel(labels[i]+' '+units[i])
        ## we then set the xlabel to Filter as in the database it is not capitalized as it should be. 
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
coloruse = {'u':'#3f7412','g':'#FF00FF','r':'#FF0000','i':'#0077BB','z':'#B22222','y':'#FFA500'}
#grizy



     
