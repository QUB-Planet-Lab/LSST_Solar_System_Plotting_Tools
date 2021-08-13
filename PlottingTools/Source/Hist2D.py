from Functions import *
import DataAccessLayer as dal
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
                        title='',filename=None,DateInterval =1,KeepData=False,ShowPlot=True,
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
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''),horizontalalignment='center')
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
                plt.title(title+' Filter: '+filter[0]+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''),horizontalalignment='center')
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
        plt.suptitle(title+' '+str(DateorMJD(MJD=startdate)).replace('18:00:00.000','')+'- '+str(DateorMJD(MJD=float(enddate))).replace('18:00:00.000',''),horizontalalignment='center')

    if (filename is not None):
        SavePlot(filename ,dict(),ShowPlot)
    else:
        SavePlot(title +'-'+xyscale[2]+'-iqea2DHist',dict(),ShowPlot)
 
    if (KeepData == True):
        return DataFrame

  

def iqea_hist_2d_plot(date=None,day=None,month=None,year=None,title='',filename=None,DateInterval =1,KeepData=False,
                      ShowPlot=True,DataFrame=None,plots = 'iqea',startdate=None, enddate=None, a_min=None, a_max=None,
                      q_min=None, q_max=None, i_min=None, i_max=None, e_min=None, e_max=None):
   
    arguments = [date,day,month,year,title,filename,DateInterval,KeepData, ShowPlot]
    usefulplots = [['q','a'],['a'],['q','a']]
    labels = {'i': 'inclination (degrees)','q': 'perihelion (au)','e' :'eccentricity','a': 'semimajor axis (au)'}
    QueryNum=7
    if (startdate is None and enddate is None): 
        QueryNum = 8
    if DataFrame is None:
        DataFrame = Queries(startdate,enddate,None,None,QueryNum,a_min,a_max,q_min,q_max,i_min,i_max , e_min, e_max)

    for i,yaxis in enumerate(plots):
        if yaxis == 'i': 
            for xaxis in usefulplots[0]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,'incl',labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
        if yaxis == 'q':
            for xaxis in usefulplots[1]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
        if yaxis == 'e': 
            for xaxis in usefulplots[2]:
                if filename is not None: 
                    name =filename+'-'+labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]
                    arguments[5]=name
                iqeaHistogramPlot2D(DataFrame=DataFrame,xyscale=[xaxis,yaxis,labels[xaxis].split(' ')[0]+'-'+labels[yaxis].split(' ')[0]],xylabels=[labels[xaxis],labels[yaxis]],*arguments)   
                arguments[5]=filename
    if KeepData: return DataFrame
 
