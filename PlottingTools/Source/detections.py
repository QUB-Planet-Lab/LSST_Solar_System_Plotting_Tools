from typing import Optional, Literal


from objects_in_field import objects_in_field

from database import db
from database.validators import validate_times, validate_filters
from database.schemas import diasource, sssource, mpcorb
from database.conditions import create_orbit_conditions
from database.format_time import format_times
from database.empty_response import empty_response

from sqlalchemy import select

import pandas as pd
import numpy as np

from plots import ScatterPlot, Histogram2D, HexagonalPlot, HistogramPlot, BarPlot


from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS
from plots.symbols import DEGREE


from Barcharts import MonthlyHelioDistHist, YearlyHelioDistHist, Weekly24hrHist, HelioDistHist

from Functions import Queries, DateorMJD

import warnings

from orbital_element_distributions import eccentricity, inclination, semi_major_axis, perihelion 


from matplotlib import patches

# from previous years

ELEMENTS = {'e' : {'label': 'Eccentricity','unit' : None},\
            'a' : {'label': 'Semi-Major axis', 'unit': 'au'},\
            'q' : {'label': 'Perihelion', 'unit': 'au'}, \
            'incl' : {'label' : 'Inclination', 'unit' : DEGREE}
           }
TIMEFRAME = ['daily', 'monthly', 'yearly']


class Detections():
    def __init__(
        self,
        start_time,
        end_time,
        filters: Optional[list] = None
        ):
        
        self.start_time, self.end_time = validate_times(start_time = start_time, end_time = end_time)
        
        
        if self.start_time is None or self.end_time is None:
            raise("A start_time and an end_time must be specified")
            
        if filters:
            self.filters = validate_filters(filters)
        else:
            self.filters = None
            
    def filter_conditions(self, filters, conditions):
                
        if filters:
            filters = validate_filters(filters)

            if self.filters and self.filters != filters:
                msg = f"Filters have already been specified when Detections was initialised. Initialised filters included: {self.filters}. Overiding filters for this query to include the specified most recent input: {filters}."
                warnings.warn(msg)
            if filters:        
                conditions.append(diasource.c['filter'].in_(filters))
       
        else:
            if self.filters:
                filters = self.filters # for internal use in the function
                conditions.append(diasource.c['filter'].in_(self.filters))
                
        return filters, conditions       
    
    
    
    
    @staticmethod
    def add_planets(ax, xlim):
        planets = {
            0.387 : 'mercury',
            0.723 : 'venus',
            1 : 'earth',
            1.524: 'mars',
            5.203 : 'jupiter',
            9.540 : 'saturn',
            19.18 : 'uranus',
            30.06 : 'neptune'
        }
        
        for dist in planets.keys():
            if dist < xlim:
                ax.add_patch(patches.Circle((0,0), radius = dist, fill = False, edgecolor="black"))
        
    
    def heliocentric_view(
        self,
        #split into multiplot
        min_hd : float = None,
        max_hd : float = None,
        
        filters: Optional[list] = None,
        title : Optional[str] = None,
        projection: Optional[Literal['2d', '3d']] = '2d',
        
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
        # validate min_hd, max_hd
        cols = [
                diasource.c['filter'],
                diasource.c['midpointtai'], 
                sssource.c['heliocentricx'],
                sssource.c['heliocentricy'],
                sssource.c['heliocentricz'],
                diasource.c['mag']
               ]

        conditions = []

        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        
            
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)
        
        if min_hd:
            conditions.append(sssource.c['heliocentricdist'] >= min_hd)
        
        if max_hd:
            conditions.append(sssource.c['heliocentricdist'] <= max_hd)
            
        
        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
        
        stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
                 stmt
        )

        if df.empty:
            return empty_response(
                start_time = self.start_time,
                end_time = self.end_time,
                filters = filters,
                #**orbital_elements
            )
        
        
        if projection:
            projection = projection.lower()
            
            if filters:
                lc = ScatterPlot(data = pd.DataFrame(columns = df.columns.values) , x ="heliocentricx", y = "heliocentricy", z="heliocentricz" , projection = projection, library = library, cache_data = cache_data, data_copy = df)

                if projection == "3d":
                        lc.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black") ## add sun and earth?
                else:
                        lc.ax.scatter(x = [0], y = [0], c = "black") ## add sun and earth?

                for _filter in filters:
                    df_filter = df[df['filter'] == _filter]

                    if not df_filter.empty:

                        if projection == "2d":
                            lc.ax.scatter(x = df_filter['heliocentricx'] , y = df_filter['heliocentricy'], c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])

                        elif projection == '3d':
                            lc.ax.scatter(xs = df_filter['heliocentricx'] , ys = df_filter['heliocentricy'], zs=df_filter['heliocentricz'] ,c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])
                            lc.ax.legend(loc="upper right")
                lc.ax.legend()
            else:
                if projection == '2d':
                    lc = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data)
                    lc.ax.scatter(x = [0], y = [0], c = "black")
                    
                elif projection == '3d':
                    lc = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", z = "heliocentricz", projection = '3d', library = library, cache_data = cache_data)
                    lc.ax.scatter(xs = [0], ys = [0], zs=[0] , c = "black")
                    
        lc.ax.set_xlabel("Heliocentric X (au)")
        lc.ax.set_ylabel("Heliocentric Y (au)")
        
        
        if projection == "3d":
            lc.ax.set_zlabel("Heliocentric Z (au)")
        lc.ax.set_title(title if title else f"")            
        if max_hd:
            lc.ax.set_xlim(-(max_hd), max_hd)
            lc.ax.set_ylim(-(max_hd), max_hd)
            lc.fig.set_figwidth(7)
            lc.fig.set_figheight(7)
        
        if add_planets and projection != "3d":
            
            df_max_x = abs(df['heliocentricx'].max()) 
            df_min_x = abs(df['heliocentricx'].min())
            
            df_max_y = abs(df['heliocentricy'].max()) 
            df_min_y = abs(df['heliocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
   
            
            self.add_planets(ax = lc.ax, xlim = df_max if df_max >= df_min else df_min)
        
        return lc    
    
    def single_heliocentric_plots(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        min_hd: Optional[float] = None,
        max_hd: Optional[float] = None,
        add_planets: Optional[bool] = False

    ):
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_view(filters = [_filter], cache_data = cache_data, min_hd = min_hd, max_hd = max_hd, add_planets = add_planets))
    
        return plots
    
    def heliocentric_histogram(
        self,
        min_hd : float = None,
        max_hd : float = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = False,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False

    ):
        # validate min_hd, max_hd
        #start = time.time()
        cols = [
            diasource.c['filter'],
            diasource.c['midpointtai'], 
            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],
            diasource.c['mag']
           ]

        conditions = []


        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        if min_hd:
            conditions.append(sssource.c['heliocentricdist'] >= min_hd)

        if max_hd:
            conditions.append(sssource.c['heliocentricdist'] <= max_hd)


        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)

        stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
             stmt
        )

        if df.empty:
            return empty_response(
                start_time = self.start_time,
                end_time = self.end_time,
            )


        lc = Histogram2D(data = df, x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data, xlabel = "Heliocentric X (au)", ylabel = "Heliocentric Y (au)", marginals = marginals )
        #lc.ax.scatter(x = [0], y = [0], c = "black")

        if marginals:
            
            #lc.ax.set_title(title if title else f"")            

            lc.ax[0].set_xlim(-(max_hd), max_hd)
            lc.ax[0].set_ylim(-(max_hd), max_hd)
        #lc.fig.set_figwidth(12)
        #lc.fig.set_figheight(12)
        
        if add_planets:
            df_max_x = abs(df['heliocentricx'].max()) 
            df_min_x = abs(df['heliocentricx'].min())
            
            df_max_y = abs(df['heliocentricy'].max()) 
            df_min_y = abs(df['heliocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
   
            
            self.add_planets(ax = lc.ax[0], xlim = df_max if df_max >= df_min else df_min)
        
            
        return lc   

            
    def heliocentric_hexplot(
        self,
        #split into multiplot
        min_hd : float = None,
        max_hd : float = None,
        
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
        
    ):
        # validate min_hd, max_hd
        #start = time.time()
        cols = [
            diasource.c['filter'],
            diasource.c['midpointtai'], 
            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],
            diasource.c['mag']
           ]

        conditions = []


        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        if min_hd:
            conditions.append(sssource.c['heliocentricdist'] >= min_hd)

        if max_hd:
            conditions.append(sssource.c['heliocentricdist'] <= max_hd)


        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)

        stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
             stmt
        )

        if df.empty:
            return empty_response(
                start_time = self.start_time,
                end_time = self.end_time,
            )


        lc = HexagonalPlot(data = df, x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data, xlabel = "Heliocentric X (au)", ylabel = "Heliocentric Y (au)")
        #lc.ax.scatter(x = [0], y = [0], c = "black")

        if marginals:
            
            #lc.ax.set_title(title if title else f"")            

            lc.ax[0].set_xlim(-(max_hd), max_hd)
            lc.ax[0].set_ylim(-(max_hd), max_hd)
        
        if add_planets:
            df_max_x = abs(df['heliocentricx'].max()) 
            df_min_x = abs(df['heliocentricx'].min())
            
            df_max_y = abs(df['heliocentricy'].max()) 
            df_min_y = abs(df['heliocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
   
            self.add_planets(ax = lc.ax[0], xlim = df_max if df_max >= df_min else df_min)
        
        return lc  
        
    
    def topocentric_view(
        self,
        #split into multiplot
        min_hd : float = None,
        max_hd : float = None,
        
        
        filters: Optional[list] = None,
        title : Optional[str] = None,
        projection: Optional[Literal['2d', '3d']] = '2d',
        
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets : Optional[bool] = False
        
    ):
        # validate min_hd, max_hd
        #start = time.time()
        cols = [
                diasource.c['filter'],
                diasource.c['midpointtai'], 
                sssource.c['topocentricx'],
                sssource.c['topocentricy'],
                sssource.c['topocentricz'],
                diasource.c['mag']
               ]

        conditions = []

        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        

        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)
        
        if min_hd:
            conditions.append(sssource.c['heliocentricdist'] >= min_hd)
        
        if max_hd:
            conditions.append(sssource.c['heliocentricdist'] <= max_hd)
            
        
        
        stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
                 stmt
        )

        if df.empty:
            return empty_response(
                start_time = self.start_time,
                end_time = self.end_time,
                filters = filters,
                #**orbital_elements
            )
        
        
        if projection:
            projection = projection.lower()
            
            if filters:
                lc = ScatterPlot(data = pd.DataFrame(columns = df.columns.values) , x ="topocentricx", y = "topocentricy", z="heliocentricz" , projection = projection, library = library, cache_data = cache_data, data_copy = df)

                if projection == "3d":
                        lc.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black") ## add sun and earth?
                else:
                        lc.ax.scatter(x = [0], y = [0], c = "black") ## add sun and earth?

                for _filter in filters:
                    df_filter = df[df['filter'] == _filter]

                    if not df_filter.empty:

                        if projection == "2d":
                            lc.ax.scatter(x = df_filter['topocentricx'] , y = df_filter['topocentricy'], c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])

                        elif projection == '3d':
                            lc.ax.scatter(xs = df_filter['topocentricx'] , ys = df_filter['topocentricy'], zs=df_filter['heliocentricz'] ,c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])
                            lc.ax.legend(loc="upper right")
                lc.ax.legend()
            else:
                if projection == '2d':
                    lc = ScatterPlot(data = df, x = "topocentricx", y = "topocentricy", library = library, cache_data = cache_data)
                    lc.ax.scatter(x = [0], y = [0], c = "black")
                    

                elif projection == '3d':
                    lc = ScatterPlot(data = df, x = "topocentricx", y = "topocentricy", z = "topocentricz", projection = '3d', library = library, cache_data = cache_data)
                    lc.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black")
                    
                    
        lc.ax.set_xlabel("Topocentric X (au)")
        lc.ax.set_ylabel("Topocentric Y (au)")
        
        
        if projection == "3d":
            lc.ax.set_zlabel("Topocentric Z (au)")
        lc.ax.set_title(title if title else f"")         
        
        if max_hd:
            lc.ax.set_xlim(-(max_hd), max_hd)
            lc.ax.set_ylim(-(max_hd), max_hd)
            lc.fig.set_figwidth(7)
            lc.fig.set_figheight(7)
            
        if add_planets and projection != "3d":
            df_max_x = abs(df['topocentricx'].max()) 
            df_min_x = abs(df['topocentricx'].min())
            
            df_max_y = abs(df['topocentricy'].max()) 
            df_min_y = abs(df['topocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            self.add_planets(ax = lc.ax, xlim = df_max if df_max >= df_min else df_min)
            
        return lc
    
    def single_topocentric_plots(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        min_hd : float = None,
        max_hd : float = None,
        add_planets : Optional[bool] = False

    ):
        
           
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            plots.append(self.topocentric_view(filters = [_filter], cache_data = cache_data, min_hd = min_hd, max_hd = max_hd, add_planets = add_planets))
            
        return plots
    
    def topocentric_histogram(
        self,
        #split into multiplot
        min_hd : float = None,
        max_hd : float = None,        
        title : Optional[str] = None,
        marginals: Optional[bool] = False,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
        # validate min_hd, max_hd
        #start = time.time()
        cols = [
            diasource.c['filter'],
            diasource.c['midpointtai'], 
            sssource.c['topocentricx'],
            sssource.c['topocentricy'],
            sssource.c['topocentricz'],
            diasource.c['mag']
           ]

        conditions = []


        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        if min_hd:
            conditions.append(sssource.c['heliocentricdist'] >= min_hd)

        if max_hd:
            conditions.append(sssource.c['heliocentricdist'] <= max_hd)


        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)

        stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
             stmt
        )

        if df.empty:
            return empty_response(
                start_time = self.start_time,
                end_time = self.end_time,
            )


        lc = Histogram2D(data = df, x = "topocentricx", y = "topocentricy", library = library, cache_data = cache_data, xlabel = "Topocentric X (au)", ylabel = "Topocentric Y (au)", marginals = marginals)
        #lc.ax.scatter(x = [0], y = [0], c = "black")

        if marginals:
            
            #lc.ax.set_title(title if title else f"")            

            lc.ax[0].set_xlim(-(max_hd), max_hd)
            lc.ax[0].set_ylim(-(max_hd), max_hd)
        #lc.fig.set_figwidth(12)
        #lc.fig.set_figheight(12)

        if add_planets:
            df_max_x = abs(df['topocentricx'].max()) 
            df_min_x = abs(df['topocentricx'].min())
            
            df_max_y = abs(df['topocentricy'].max()) 
            df_min_y = abs(df['topocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
           
            
            self.add_planets(ax = lc.ax[0], xlim = df_max if df_max >= df_min else df_min)
        return lc
    
    def topocentric_hexplot(
        self,
        #split into multiplot
        min_hd : float = None,
        max_hd : float = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
        # validate min_hd, max_hd
        #start = time.time()
        cols = [
            diasource.c['filter'],
            diasource.c['midpointtai'], 
            sssource.c['topocentricx'],
            sssource.c['topocentricy'],
            sssource.c['topocentricz'],
            diasource.c['mag']
           ]

        conditions = []


        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        if min_hd:
            conditions.append(sssource.c['heliocentricdist'] >= min_hd)

        if max_hd:
            conditions.append(sssource.c['heliocentricdist'] <= max_hd)


        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)

        stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
             stmt
        )

        if df.empty:
            return empty_response(
                start_time = self.start_time,
                end_time = self.end_time
            )


        lc = HexagonalPlot(data = df, x = "topocentricx", y = "topocentricy", library = library, cache_data = cache_data, xlabel = "Topocentric X (au)", ylabel = "Topocentric Y (au)")
        #lc.ax.scatter(x = [0], y = [0], c = "black")
        if marginals:
            
            #lc.ax.set_title(title if title else f"")            

            lc.ax[0].set_xlim(-(max_hd), max_hd)
            lc.ax[0].set_ylim(-(max_hd), max_hd)
            
    
        
        #lc.fig.set_figwidth(12)
        #lc.fig.set_figheight(12)
        
        if add_planets:
            df_max_x = abs(df['topocentricx'].max()) 
            df_min_x = abs(df['topocentricx'].min())
            
            df_max_y = abs(df['topocentricy'].max()) 
            df_min_y = abs(df['topocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            
            self.add_planets(ax = lc.ax[0], xlim = df_max if df_max >= df_min else df_min)
          
        return lc

        
    @staticmethod
    def orbital_relations(   
        x : Literal["incl", "q", "e", "a"],
        y : Literal["incl", "q", "e", "a"],
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        title : Optional[str] = None,
        plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
        cache_data: Optional[bool] = False,
        marginals: Optional[bool] = False,
        **orbital_elements
    ):

        conditions = []
        
        if start_time:
            conditions.append(diasource.c['midpointtai'] >= start_time)

        if end_time:
            conditions.append(diasource.c['midpointtai'] <= end_time)

        conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)

        if x == "a":
            qx = (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a')
        else:
            qx = mpcorb.c[x]

        if y == "a":
            qy = (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a')
        else:
            qy = mpcorb.c[y]

        df = db.query(
            select(
                mpcorb.c['ssobjectid'], qx , qy, diasource.c['filter']).join(
                diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']

            ).where(
                    *conditions
            )
        )

        if df.empty:
            return empty_response(
                    start_time = start_time,
                    end_time = end_time,
                    **orbital_elements
                )

        if plot_type not in ["scatter", "2d_hist", "2d_hex"]:
            raise Exception("Plot type must be scatter, 2d_hist, 2d_hex")
        
        xlabel = ELEMENTS[x]['label'] + (f" ({ELEMENTS[x]['unit']})" if ELEMENTS[x]['unit'] else '')
        
        ylabel = ELEMENTS[y]['label'] + (f" ({ELEMENTS[x]['unit']})" if ELEMENTS[y]['unit'] else '')
        
        
        
        
        if plot_type == "scatter":
            hp = ScatterPlot(data = df, x=x, y=y, xlabel=xlabel, ylabel=ylabel, title = title)

        if plot_type == "2d_hex":

            hp = HexagonalPlot(data = df, x = x, y = y, cache_data = cache_data, xlabel=xlabel, ylabel=ylabel, title = title)

        if plot_type == "2d_hist":
            hp = Histogram2D(data = df, x = x, y = y, cache_data = cache_data, xlabel=xlabel, ylabel=ylabel, title = title, marginals = marginals)
            
       

        return hp
    
    def orbital_relations_scatter(
        self,
        x : Literal["incl", "q", "e", "a"],
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        return self.orbital_relations(
            x = x,
            y = y,
            start_time = self.start_time,
            end_time = self.end_time,
            title = title,
            cache_data = cache_data,
            plot_type = "scatter",
            **orbital_elements
        )
    
    def orbital_relations_histogram(
        self,
        x : Literal["incl", "q", "e", "a"],
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        cache_data: Optional[bool] = False,
        marginals: Optional[bool] = False,
        **orbital_elements
    ):
        return self.orbital_relations(
            x = x,
            y = y,
            start_time = self.start_time,
            end_time = self.end_time,
            title = title,
            cache_data = cache_data,
            plot_type = "2d_hist",
            marginals = marginals,
            **orbital_elements
        )
    
    def orbital_relations_hexplot(
        self,
        x : Literal["incl", "q", "e", "a"],
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        return self.orbital_relations(
            x = x,
            y = y,
            start_time =self.start_time,
            end_time = self.end_time,
            title = title,
            cache_data = cache_data,
            plot_type = "2d_hex",
            **orbital_elements
        )
    
    
    def detection_distributions(
        self,
        title : Optional[str] = None,
        timeframe : Literal["daily", "monthly", "yearly"] = "daily",
        time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        # slow - can cut the list
        if timeframe not in TIMEFRAME:
            raise Exception(f"Timeframe must be one of {TIMEFRAME}")


        conditions = create_orbit_conditions(**orbital_elements)

        df = db.query(
            select(diasource.c['midpointtai']).join(mpcorb, mpcorb.c['ssobjectid'] == diasource.c['ssobjectid']).distinct(diasource.c['ssobjectid']).where(
                diasource.c['midpointtai'] >= self.start_time,
                diasource.c['midpointtai'] <= self.end_time,
                *conditions
            )
        )

        if timeframe == "daily":
             df['datetime'] = [date[0:10] for date in format_times(df['midpointtai'].tolist(), _format="ISO")]

        if timeframe == "monthly":
             df['datetime'] = [date[0:7] for date in format_times(df['midpointtai'].tolist(), _format="ISO")]

        #df = df.sort_values(by = ['midpointtai'], ascending=True)

        if timeframe == "yearly":
            df['datetime'] = [date[0:4] for date in format_times(df['midpointtai'].tolist(), _format="ISO")]

        df = df.sort_values(by = ['midpointtai'], ascending=True)

        hp = HistogramPlot(data = df, x="datetime", library = "seaborn", ylabel = "Count") #, xbins = bins)
    
        hp.ax.set(yscale="log")
        hp.ax.set_xlabel(xlabel = "Datetime", labelpad = 6) # check
        hp.fig.suptitle(title if title else f"Detection distributions")
        
        hp.fig.autofmt_xdate()

        '''
        hp.ax.set_xlabel("Date")
        hp.ax.set_ylabel("No. of Detections")

        if time_format == "ISO":
            hp.ax.set_xticks(ticks = bins, labels = [date[0:10] for date in format_times(bins, _format="ISO")])

        '''  
        return hp
    
    
    def daily_detection_distributions(
        self,
        DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]]
):
        KeepData = False
        interval = int(self.end_time) - int(self.start_time)

        dates = np.linspace(0, interval-1, interval)
        counters = np.ndarray((len(dates)*len(DistanceMinMax),3))

        ticks = np.ndarray.tolist(np.linspace(0, interval,interval+1))


        count=0

        for i,offset in enumerate(dates):
            distances = []    

            for MinMax in DistanceMinMax:
                distances+=[[self.start_time+offset, self.start_time+offset+1, *MinMax,3]]

            for j in range(len(distances)):
                df = Queries(*distances[j])
                
                counters[count,:] = [offset+ self.start_time,df['count'].values[0],j]

                count += 1

        NewData =  pd.DataFrame(data=counters, columns=['Date','Detections','distance'])

        legend = [str(distance[2])+'-'+str(distance[3])+' (au)' for i,distance in enumerate(distances)]

        bp = BarPlot(data = NewData, x = "Date", y = "Detections", hue="distance", xlabel = "Date", ylabel = "Detection count")
        
        #bp.fig.set_size_inches(3*DateInterval,4)

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

        ProperDateLabels = [DateorMJD(MJD=date,ConvertToIso=False).to_value(format='iso',subfmt='date') for date in dates+self.start_time]

        bp.ax.set_xticklabels(ProperDateLabels)

        bp.ax.set(yscale="log")

        return bp
    
    @staticmethod
    def population_detection_distributions(
        # split into populations
        start_time : Optional[float] = None, end_time : Optional[float] = None,
        title : Optional[str] = None,
        timeframe : Literal["daily", "monthly", "yearly"] = "daily",
        time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        st, et = format_times([start_time, end_time], _format="ISO")
                
        
        hp = HistogramPlot(data = pd.DataFrame(columns = ["count", "date"]), x = "date")
        hp.fig.clear()
        
        #set data
        if timeframe == "daily":
            days = int(et[8:10]) - int(st[8:10])
            hp.ax = HelioDistHist(start_time = start_time, end_time = end_time, date = start_time, DateInterval = days, DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3],[3,3.5],[3.5,4]],  KeepData = False)
            
                           
        if timeframe == "monthly":
            # note includes entire month
            months = int(et[5:7]) - int(st[5:7]) + 1
            hp.plot = MonthlyHelioDistHist(date= start_time,filename='monthly_histogram',DateInterval = months ,KeepData=False,ShowPlot=False,DistanceMinMax=[[30,80], [80, 100]])
        
        if timeframe == "yearly":
            #note includes entire year
            years = int(et[0:4]) - int(st[0:4]) + 1
            
            hp.plot = YearlyHelioDistHist(date=start_time, filename='yearly_histogram',DateInterval = years ,KeepData=False,ShowPlot=True,DistanceMinMax=[[30,80], [80, 100]])

        hp.ax = hp.plot

        return hp
      
                         
    def orbital_distributions(
        self,
        parameter : Literal["e", "incl", "q", "a"],
        filters: Optional[list] = None,
        plot_type: Literal["BOX", "VIOLIN", "BOXEN"] = 'BOX',
        title : Optional[str] = None,
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        parameter = parameter.lower()
        
        if parameter not in ["e", "incl", "q", "a"]:
            raise Exception(f"Orbital parameter must be one of: e, incl, q, a")
            
        args = dict(
            filters = filters,
            plot_type = plot_type,
            start_time = self.start_time,
            end_time = self.end_time,
            cache_data = cache_data,
            title = title,
            **orbital_elements
        )
        
        if parameter == "e":
            return eccentricity(
                **args
            )
        if parameter == "incl":
            return inclination(
                **args
            )
        if parameter == "a":
            return semi_major_axis(
                **args
            )
        if parameter == "q":
            return perihelion(
                **args
            )
    
    def all_orbital_distributions(
        self,
        filters: Optional[list] = None,
        plot_type: Literal["BOX", "VIOLIN", "BOXEN"] = 'BOX',
        title : Optional[str] = None,
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        plots = []
        
        args = dict(
            filters = filters,
            plot_type = plot_type,
            cache_data = cache_data,
            title = title,
            **orbital_elements
        )
        
        for element in ["e", "incl", "q", "a"]:
            plots.append(
                self.orbital_distributions(
                    parameter = element,
                    **args
                )
            )
        return plots

from astropy.time import Time
from sqlalchemy import text
import seaborn as sns


def monthly_detection_distribution(
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
    

'''
        start_time : str = "2024-01",
        end_time : str = "2024-03",
        distances = [[80, 81]]
        ):
    
    
    if len(start_time) != 7 or len(end_time) != 7:
        raise Exception("Invalid input times. Format is YYYY-MM")

    if start_time[4] != '-' or end_time[4] != '-':
        raise Exception("Invalid input times. Format is YYYY-MM")
    
    try:
        isinstance(int(start_time[0:4]), int)
        isinstance(int(end_time[0:4]), int)
        isinstance(int(start_time[5:8]), int)
        isinstance(int(end_time[5:8]), int)
        
    except:
        raise Exception("Invalid input times. Format is YYYY-MM")
    
    start_time = start_time + '-01' # default to first of the month
    
        
    end_time = f"{end_time}-01"
    years = int(end_time[0:4]) - int(start_time[0:4])
    
    months = int(end_time[5:7]) - int(start_time[5:7])
    
    
    if years < 0:
        raise Exception("Invalid dates input. End time must be greater than start time")
        
    if years == 0:
        if months < 0:
            raise Exception("Invalid dates input. End time must be greater than start time")
            
    iso_times = np.arange(np.datetime64(start_time),
                  np.datetime64(end_time), np.timedelta64(1, 'M'), dtype='datetime64[M]')

    mjd_times = format_times([str(time) + "-01" for time in iso_times], _format="MJD")
    
    # create queries
    
    #df cols, count, distance, date
    
    #distances

    time_ranges = [[mjd_times[i], mjd_times[i + 1]] for i in range(len(mjd_times) - 1)]
    queries  = []
    for dist in distances:
        for pair in time_ranges:
            queries.append(
                text(f"""SELECT COUNT(*)
               FROM
               diasources, sssources
               WHERE
               midpointtai BETWEEN  {pair[0]} AND {pair[1]}
               AND
               sssources.heliocentricdist BETWEEN {dist[0]} AND {dist[1]}
               AND
               (diasources.diasourceid=sssources.diasourceid)
            """)
            )
    print(queries)
    x = db.transaction(
        queries
    )
        
    print(x)
'''

def yearly_detection_distribution(
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