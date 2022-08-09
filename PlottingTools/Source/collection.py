from database import db
from database.validators import validate_orbital_elements, validate_times, validate_filters
from database.schemas import sssource, mpcorb, diasource
from database.conditions import create_orbit_conditions

from orbital_element_distributions import _orbital_relations, eccentricity, perihelion, semi_major_axis, inclination, _tisserand_relations

from objects_in_field import objects_in_field

from observations import _detection_distributions

from typing import Optional, Literal

from sqlalchemy import select, func, distinct, column
import warnings

from matplotlib import patches
import pandas as pd

from plots import ScatterPlot, HexagonalPlot, Histogram2D
from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS

PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']
ORB_PARAMS = ["eccentricity", "perihelion", "semi_major_axis", "inclination"]

class Objects():
    def __init__(self,
                 start_time, 
                 end_time, 
                 filters: Optional[list] = None,
                 lazy_loading: Optional[bool] = True,  
                 **orbital_elements):
         
        self.lazy_loading = lazy_loading
        
        self.min_a, self.max_a, self.min_incl, self.max_incl, self.min_peri, self.max_peri, self.min_e, self.max_e, self.min_hd, self.max_hd = validate_orbital_elements(**orbital_elements)
        
        self.start_time, self.end_time = validate_times(start_time = start_time, end_time = end_time)
        
        
        self.conditions = []
        
        if self.start_time:
            self.conditions.append(diasource.c['midpointtai'] >= self.start_time)
    
        if self.end_time:
            self.conditions.append(diasource.c['midpointtai'] <= self.end_time)
        
        
        self.conditions = create_orbit_conditions(conditions = self.conditions, **orbital_elements)
        
                
        a_J = 5.2038 # au
        
        
        tisserand = (a_J / (mpcorb.c['q'] / (1 - mpcorb.c['e'])) + 2 * func.cos(mpcorb.c['incl']) * func.sqrt((mpcorb.c['q'] / (1 - mpcorb.c['e'])) / a_J * (1 - func.power(mpcorb.c['e'], 2)))).label("tisserand")

        self.cols = [
            diasource.c['midpointtai'],
            diasource.c['filter'],
            diasource.c['ssobjectid'],

            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],

            mpcorb.c['q'],
            mpcorb.c['e'],
            mpcorb.c['incl'],
            (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a'),

            tisserand
        ]
        
        self.table_columns = {
            'midpointtai' : diasource.c['midpointtai'],
            'filter' : diasource.c['filter'],
            'ssobjectid' : diasource.c['ssobjectid'],
            'heliocentricx': sssource.c['heliocentricx'],
            'heliocentricy': sssource.c['heliocentricy'],
            'heliocentricz' : sssource.c['heliocentricz'],
            
            'topocentricx': sssource.c['topocentricx'],
            'topocentricy': sssource.c['topocentricy'],
            'topocentricz' : sssource.c['topocentricz'],

            'q' : mpcorb.c['q'],
            'e' : mpcorb.c['e'],
            'incl' : mpcorb.c['incl'],
            'a': (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a'),

            'tisserand' : tisserand
        }
        
        if filters:
            self.filters = validate_filters(filters)
        else:
            self.filters = None
        
        if lazy_loading == False:
            self.data = self.get_data(list(self.table_columns.keys()))
        else:
            self.data = None
            
    def filter_conditions(self, filters, conditions):
                
        if filters:
            filters = validate_filters(filters)

            if self.filters and self.filters != filters:
                #msg = f"Filters have already been specified when Detections was initialised. Initialised filters included: {self.filters}. Overiding filters for this query to include the specified most recent input: {filters}."
                #warnings.warn(msg)
                pass
            if filters:        
                conditions.append(diasource.c['filter'].in_(filters))
       
        else:
            if self.filters:
                filters = self.filters # for internal use in the function
                conditions.append(diasource.c['filter'].in_(self.filters))
                
        return filters, conditions
    
    def get_data(self, cols):
        # THIS DISTINCT WORKS
        
        df = db.query(
                    select(
                        *[self.table_columns[col] for col in cols]
                    ).join(
                        diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']
                    ).join(
                        sssource, sssource.c['ssobjectid'] == mpcorb.c['ssobjectid']
                    ).distinct(mpcorb.c['ssobjectid'], diasource.c['filter']).where(*self.conditions)
                )
        
        if self.data is None:
            self.data = df
        
        else:
            self.data = self.data.merge(
                df,
                on = ['ssobjectid', 'midpointtai']
            )
            
        return self.data
    
    def check_data(self, cols_required):
        
        if self.lazy_loading:
            if self.data is None:
                df = self.get_data(cols_required) 
                
            else:
                c = ['ssobjectid', 'midpointtai']
                for col in cols_required:
                   
                    if (col in self.data.columns):
                        pass
                        
                    else:
                        c.append(col)
                    
                df = self.get_data(c)                        
        else:
            df = self.data #self.get_data(list(self.table_columns.keys()))
        return df
    
    
    
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
        filters: Optional[list] = None,
        title : Optional[str] = None,
        projection: Optional[Literal['2d', '3d']] = '2d',
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
        
        df = self.check_data(
            ['ssobjectid', 'filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid', 'midpointtai']
        )
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
                
        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
        
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
            
        df_max_x = abs(df['heliocentricx'].max()) 
        df_min_x = abs(df['heliocentricx'].min())

        df_max_y = abs(df['heliocentricy'].max()) 
        df_min_y = abs(df['heliocentricy'].min())

        df_max = df_max_x if df_max_x >= df_max_y else df_max_y
        df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            
        _max = df_max if df_max >= df_min else df_min
        
        if add_planets and projection != "3d":
            self.add_planets(ax = lc.ax, xlim = df_max if df_max >= df_min else df_min)
        
        lc.ax.set_xlim(-(_max), _max)
        lc.ax.set_ylim(-(_max), _max)
        lc.fig.set_figwidth(7)
        lc.fig.set_figheight(7)#
        
        return lc    
    
    def single_heliocentric_plots(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_view(filters = [_filter], cache_data = cache_data, add_planets = add_planets))
        
        return plots
    
    def heliocentric_histogram(
        self,
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):

        filters, _ = self.filter_conditions(filters = filters, conditions = [])
              
        df = self.check_data(
            ['ssobjectid', 'filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid', 'midpointtai']
        )

        lc = Histogram2D(data = df[df['filter'].isin(filters)], x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data, xlabel = "Heliocentric X (au)", ylabel = "Heliocentric Y (au)", marginals = marginals)
        
        #lc.ax.scatter(x = [0], y = [0], c = "black")

        if marginals:
            #lc.ax.set_title(title if title else f"")            
            #lc.ax[0].set_xlim(-(max_hd), max_hd)
            #lc.ax[0].set_ylim(-(max_hd), max_hd)
            pass
        #lc.fig.set_figwidth(12)
        #lc.fig.set_figheight(12)
        
        if add_planets:
            df_max_x = abs(df['heliocentricx'].max()) 
            df_min_x = abs(df['heliocentricx'].min())
            
            df_max_y = abs(df['heliocentricy'].max()) 
            df_min_y = abs(df['heliocentricy'].min())
            
            df_max = df_max_x if df_max_x >= df_max_y else df_max_y
            df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            ax = lc.ax[0] if marginals else lc.ax
            
            self.add_planets(ax = ax, xlim = df_max if df_max >= df_min else df_min)
        
            
        return lc   

    def single_heliocentric_histogram(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False

    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_histogram(filters = [_filter], cache_data = cache_data, add_planets = add_planets))
    
        return plots
        
    def heliocentric_hexplot(
        self,    
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
        
    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
     
        
        df = self.check_data(
            ['ssobjectid', 'filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid', 'midpointtai']
        )
        

        lc = HexagonalPlot(data = df[df['filter'].isin(filters)], x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data, xlabel = "Heliocentric X (au)", ylabel = "Heliocentric Y (au)")
        #lc.ax.scatter(x = [0], y = [0], c = "black")

        
        df_max_x = abs(df['heliocentricx'].max()) 
        df_min_x = abs(df['heliocentricx'].min())

        df_max_y = abs(df['heliocentricy'].max()) 
        df_min_y = abs(df['heliocentricy'].min())

        df_max = df_max_x if df_max_x >= df_max_y else df_max_y
        df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            
        _max = df_max if df_max >= df_min else df_min
        
        if add_planets:
            self.add_planets(ax = lc.ax[0], xlim = df_max if df_max >= df_min else df_min)
        
        if marginals:
            lc.ax[0].set_xlim(-(_max), _max)
            lc.ax[0].set_ylim(-(_max), _max)

        else:    
            lc.ax.set_xlim(-(_max), _max)
            lc.ax.set_ylim(-(_max), _max)

        lc.fig.set_figwidth(7)
        lc.fig.set_figheight(7)
        
        return lc  
        
    
    def single_heliocentric_hexplot(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False

    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_hexplot(filters = [_filter], cache_data = cache_data, add_planets = add_planets, title = f"{_filter} Filter"))
        
        return plots
    
    def topocentric_view(
        self,        
        filters: Optional[list] = None,
        title : Optional[str] = None,
        projection: Optional[Literal['2d', '3d']] = '2d',
        
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets : Optional[bool] = False
        
    ):
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
      
        #conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
        
        df = self.check_data(
            ['ssobjectid', 'filter', 'topocentricx', 'topocentricy', 'topocentricz', 'ssobjectid', 'midpointtai']
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
        
        df_max_x = abs(df['topocentricx'].max()) 
        df_min_x = abs(df['topocentricx'].min())

        df_max_y = abs(df['topocentricy'].max()) 
        df_min_y = abs(df['topocentricy'].min())

        df_max = df_max_x if df_max_x >= df_max_y else df_max_y
        df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            
        _max = df_max if df_max >= df_min else df_min
        
        if add_planets and projection != "3d":
            self.add_planets(ax = lc.ax, xlim = df_max if df_max >= df_min else df_min)
        
        lc.ax.set_xlim(-(_max), _max)
        lc.ax.set_ylim(-(_max), _max)
        lc.fig.set_figwidth(7)
        lc.fig.set_figheight(7)#
        
            
        return lc
    
    def single_topocentric_plots(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        add_planets : Optional[bool] = False
    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            plots.append(self.topocentric_view(filters = [_filter], cache_data = cache_data, add_planets = add_planets, title = f"{_filter} Filter"))
            
        return plots
    
    def topocentric_histogram(
        self,
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
         
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
      
        df = self.check_data(
            ['ssobjectid', 'filter', 'topocentricx', 'topocentricy', 'topocentricz', 'ssobjectid', 'midpointtai']
        )
        

        lc = Histogram2D(data = df[df['filter'].isin(filters)], x = "topocentricx", y = "topocentricy", library = library, cache_data = cache_data, xlabel = "Topocentric X (au)", ylabel = "Topocentric Y (au)", marginals = marginals, title = title)
        
        df_max_x = abs(df['topocentricx'].max()) 
        df_min_x = abs(df['topocentricx'].min())

        df_max_y = abs(df['topocentricy'].max()) 
        df_min_y = abs(df['topocentricy'].min())

        df_max = df_max_x if df_max_x >= df_max_y else df_max_y
        df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            
        _max = df_max if df_max >= df_min else df_min
        
        if add_planets:
            self.add_planets(ax = lc.ax, xlim = df_max if df_max >= df_min else df_min)
            
        if marginals:
            lc.ax[0].set_xlim(-(_max), _max)
            lc.ax[0].set_ylim(-(_max), _max)
        else:
            lc.ax.set_xlim(-(_max), _max)
            lc.ax.set_ylim(-(_max), _max)
        
        lc.fig.set_figwidth(7)
        lc.fig.set_figheight(7)
        
        return lc
    
    def single_topocentric_histogram(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        add_planets : Optional[bool] = False

    ):
        
           
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            plots.append(self.topocentric_histogram(filters = [_filter], cache_data = cache_data, add_planets = add_planets, title = f"{_filter} Filter"))
            
    def topocentric_hexplot(
        self,
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        add_planets: Optional[bool] = False
    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
      
        
        df = self.check_data(
            ['ssobjectid', 'filter', 'topocentricx', 'topocentricy', 'topocentricz', 'ssobjectid', 'midpointtai']
        )
        df_filter = df[df['filter'].isin(filters)]
        if df_filter.empty:
            print("No data for plot to be made")
                  
            return 
        
        lc = HexagonalPlot(data = df[df['filter'].isin(filters)], x = "topocentricx", y = "topocentricy", library = library, cache_data = cache_data, xlabel = "Topocentric X (au)", ylabel = "Topocentric Y (au)", title = title)
        #lc.ax.scatter(x = [0], y = [0], c = "black")
        
        df_max_x = abs(df['topocentricx'].max()) 
        df_min_x = abs(df['topocentricx'].min())

        df_max_y = abs(df['topocentricy'].max()) 
        df_min_y = abs(df['topocentricy'].min())

        df_max = df_max_x if df_max_x >= df_max_y else df_max_y
        df_min = df_min_x if df_min_x >= df_min_y else df_min_y
            
            
        _max = df_max if df_max >= df_min else df_min
        
        if add_planets:
            self.add_planets(ax = lc.ax, xlim = df_max if df_max >= df_min else df_min)
        if marginals:
            lc.ax[0].set_xlim(-(_max), _max)
            lc.ax[0].set_ylim(-(_max), _max)
        else:
            lc.ax.set_xlim(-(_max), _max)
            lc.ax.set_ylim(-(_max), _max)
            
        lc.fig.set_figwidth(7)
        lc.fig.set_figheight(7)#
               
          
        return lc

    def single_topocentric_hexplot(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        add_planets : Optional[bool] = False
    ):
           
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            
            plots.append(self.topocentric_hexplot(filters = [_filter], cache_data = cache_data, add_planets = add_planets, title = f"{_filter} Filter"))

    
    
    def orbital_relations(
        self,
        x : Literal["incl", "q", "e", "a"],
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        colorbar: bool = True,
        plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
        cache_data: Optional[bool] = False
):
        
        
        df = self.check_data(
            ['ssobjectid','midpointtai', x, y]
        )


        return _orbital_relations(
            df = df[[x, y, 'ssobjectid', 'midpointtai']],
            x = x, 
            y = y,
            start_time = self.start_time, 
            end_time = self.end_time,
            plot_type = plot_type, title = title,
            cache_data = cache_data,
            min_a = self.min_a, 
            max_a = self.max_a, 
            min_incl = self.min_incl, max_incl = self.max_incl, 
            min_peri = self.min_peri, max_peri = self.max_peri, 
            min_e = self.min_e, max_e = self.max_e
       )
                           
    def orbital_relations_hexplot(
             self,
             x : Literal["incl", "q", "e", "a"],
             y : Literal["incl", "q", "e", "a"],
             title : Optional[str] = None,
             colorbar: bool = True,
             cache_data: Optional[bool] = False
    ):
        
        return self.orbital_relations(
            plot_type = "2d_hex",
            x = x,
            y = y,
            title = title,
            colorbar = True,
            cache_data = cache_data
        )
    
    def orbital_relations_scatter(
             self,
             x : Literal["incl", "q", "e", "a"],
             y : Literal["incl", "q", "e", "a"],
             title : Optional[str] = None,
             colorbar: bool = True,
             cache_data: Optional[bool] = False
    ):
        
        return self.orbital_relations(
            plot_type = "scatter",
            x = x,
            y = y,
            title = title,
            colorbar = True,
            cache_data = cache_data
        )
    
    def orbital_relations_histogram(
             self,
             x : Literal["incl", "q", "e", "a"],
             y : Literal["incl", "q", "e", "a"],
             title : Optional[str] = None,
             colorbar: bool = True,
             cache_data: Optional[bool] = False
    ):
        
        return self.orbital_relations(
            plot_type = "2d_hist",
            x = x,
            y = y,
            title = title,
            colorbar = True,
            cache_data = cache_data
        )
    
    def tisserand_relations(self,
                            y : Literal["incl", "q", "e", "a"],
                            title : Optional[str] = None,
                            plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
                            cache_data: Optional[bool] = False
                           ):
        
        df = self.check_data(
            ['ssobjectid', 'midpointtai', 'tisserand', y]
        )
        
        tr = _tisserand_relations(
            df = df[['tisserand', y, 'ssobjectid']],
            y = y,  
            #start_time = start_time if start_time else self.start_time, 
            #end_time = end_time if end_time else self.end_time, 
            title = title,
            plot_type = plot_type,
            cache_data = cache_data,
            min_a = self.min_a, 
            max_a = self.max_a,
            min_incl = self.min_incl,
            max_incl = self.max_incl,
            min_peri = self.min_peri, 
            max_peri = self.max_peri, 
            min_e = self.min_e, 
            max_e = self.max_e
       )
        '''
        tr.ax.set_xlim(left = tr.data["tisserand"].min(), right = tr.data["tisserand"].max())
        tr.ax.set_ylim(bottom =  tr.data[y].min(), top = tr.data[y].max())
        '''
        return tr
    
    def tisserand_relations_scatter(
        self,
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        
        cache_data: Optional[bool] = False
    ):
        return self.tisserand_relations(
            y = y,
            plot_type = "scatter",
            title = title,
            cache_data = cache_data
        )
    
    def tisserand_relations_hexplot(
        self,
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        cache_data: Optional[bool] = False
    ):
        return self.tisserand_relations(
            y = y,
            plot_type = "2d_hex",
            title = title,
            cache_data = cache_data
        )
        
    def tisserand_relations_histogram(
        self,
        y : Literal["incl", "q", "e", "a"],
        title : Optional[str] = None,
        cache_data: Optional[bool] = False
    ):
        return self.tisserand_relations(
            y = y,
            plot_type = "2d_hist",
            title = title,
            cache_data = cache_data
        )
        
    def orbital_param_distribution(self,
                                    parameter : Literal["e", "a", "incl", "q"],
                                    filters: Optional[list] = None,
                                    plot_type: Literal[PLOT_TYPES] = 'BOX',
                                    title : Optional[str] = None,
                                    library: Optional[str] = "seaborn",
                                    cache_data: Optional[bool] = False
                                  ):
        
        parameter = parameter.lower()
        
        if parameter not in ["e", "a", "incl", "q"]:
            raise Exception(f"Orbital parameter must be one of: e, a, incl, q")
        
        required_cols = ['ssobjectid', 'midpointtai', 'filter']
        
        if parameter == "e":
            required_cols.append("e")
        if parameter == "a":
            required_cols.append("a")
        if parameter == "incl":
            required_cols.append("incl")
        if parameter == "q":
            required_cols.append("q")
            
        df = self.check_data(
            required_cols
        )
        
        filters, self.conditions = self.filter_conditions(filters = filters, conditions = self.conditions)

        args = dict(
            filters = filters,
            plot_type = plot_type,
            #start_time = start_time if start_time else self.start_time,
            #end_time = end_time if end_time else self.end_time,
            cache_data = cache_data,
            title = title,
            library = library,
            min_a = self.min_a, 
            max_a = self.max_a,
            min_incl = self.min_incl,
            max_incl = self.max_incl,
            min_peri = self.min_peri, 
            max_peri = self.max_peri, 
            min_e = self.min_e, 
            max_e = self.max_e
        )
        
        if parameter == "e":
            return eccentricity(
                df[['filter', 'e', 'ssobjectid']],
                **args
            )
        if parameter == "incl":
            return inclination(
                df[['filter', 'incl', 'ssobjectid']], 
                **args
            )
        if parameter == "a":
            return semi_major_axis(
                df[['filter', 'a', 'ssobjectid']], 
                **args
            )
        if parameter == "q":
            return perihelion(
                df[['filter', 'q', 'ssobjectid']], 
                **args
            )
        
        #getter setter for __init__ that calls functions and updates plots
    def e_distributions(
        self,
        filters: Optional[list] = None,
        plot_type: Literal[PLOT_TYPES] = 'BOX',
        title : Optional[str] = None,
        library: Optional[str] = "seaborn",
        cache_data: Optional[bool] = False
    ):
        

        return self.orbital_param_distribution(
            parameter = "e",
            filters = filters,
            plot_type = plot_type,
            title = title,
            cache_data = cache_data,
            library = library
        )
    
    def a_distributions(
        self,
        filters: Optional[list] = None,
        plot_type: Literal[PLOT_TYPES] = 'BOX',
        title : Optional[str] = None,
        library: Optional[str] = "seaborn",
        cache_data: Optional[bool] = False
    ):
        
       

        return self.orbital_param_distribution(
            parameter = "a",
            filters = filters,
            plot_type = plot_type,
            title = title,
            cache_data = cache_data,
            library = library
        )
    def q_distributions(
        self,
        filters: Optional[list] = None,
        plot_type: Literal[PLOT_TYPES] = 'BOX',
        title : Optional[str] = None,
        library: Optional[str] = "seaborn",
        cache_data: Optional[bool] = False
    ):
        
        

            
        return self.orbital_param_distribution(
            parameter = "q",
            filters = filters,
            plot_type = plot_type,
            title = title,
            cache_data = cache_data,
            library = library
        )
    
    def incl_distributions(
        self,
        filters: Optional[list] = None,
        plot_type: Literal[PLOT_TYPES] = 'BOX',
        title : Optional[str] = None,
        library: Optional[str] = "seaborn",
        cache_data: Optional[bool] = False
    ):
        
        filters, self.conditions = self.filter_conditions(filters = filters, conditions = self.conditions)

            
        return self.orbital_param_distribution(
            parameter = "incl",
            filters = filters,
            plot_type = plot_type,
            title = title,
            cache_data = cache_data,
            library = library
        )
    
    def all_orbital_distributions(
        self,
        filters: Optional[list] = None,
        plot_type: Literal[PLOT_TYPES] = 'BOX',
        title : Optional[str] = None,
        library: Optional[str] = "seaborn",
        cache_data: Optional[bool] = False
    ):
        plots = []
        
        
        for element in ["a", "q", "incl", "e"]:
            plots.append(
                self.orbital_param_distribution(
                    parameter = element,
                    title = title,
                    cache_data = cache_data,
                    filters = filters
                )
            )
                         
        return plots
                

    def clear(self):
        self.data = None
        return
        
    