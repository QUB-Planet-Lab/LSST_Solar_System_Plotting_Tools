from typing import Optional, Literal


from objects_in_field import objects_in_field

from database import db
from database.validators import validate_times, validate_filters, validate_orbital_elements
from database.schemas import diasource, sssource, mpcorb
from database.conditions import create_orbit_conditions
from database.format_time import format_times
from database.empty_response import empty_response

from sqlalchemy import select

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from plots import ScatterPlot, Histogram2D, HexagonalPlot, HistogramPlot, BarPlot

from plots.plot import MultiPlot

from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS
from plots.symbols import DEGREE


from Barcharts import MonthlyHelioDistHist, YearlyHelioDistHist, Weekly24hrHist, HelioDistHist

from Functions import Queries, DateorMJD

from orbital_element_distributions import eccentricity, inclination, semi_major_axis, perihelion 


from matplotlib import patches

from detections_utils import _heliocentric_view, _heliocentric_histogram, _heliocentric_hexplot, _topocentric_view, _topocentric_histogram, _topocentric_hexplot

from detections_utils import monthly_detection_distributions, yearly_detection_distributions, _daily_detection_distributions


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
        filters: Optional[list] = None,
        **orbital_elements
        ):
        
        self.start_time, self.end_time = validate_times(start_time = start_time, end_time = end_time)
        
        if self.start_time is None or self.end_time is None:
            raise("A start_time and an end_time must be specified")
            
        if filters:
            self.filters = validate_filters(filters)
        else:
            self.filters = None
        
        #validate
        _ = validate_orbital_elements(**orbital_elements)
        
        self.orbital_elements = orbital_elements
        
    
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
    
    def merge_orbital_arguments(self, **orbital_elements):
        for element in self.orbital_elements:
            if element not in orbital_elements:
                orbital_elements[element] = self.orbital_elements[element]
        return orbital_elements
    
    def orbital_conditions(self, conditions, helio, **orbital_elements):

        _ = validate_orbital_elements(**orbital_elements)

        orbital_elements = self.merge_orbital_arguments(
            **orbital_elements
        )
       
        return orbital_elements, create_orbit_conditions(conditions = conditions, helio=helio, **orbital_elements)
        
       
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
        planets: Optional[bool] = False,
        **orbital_elements
    ):
        
        conditions = []
        
        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)

        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = True, **orbital_elements)
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)
               
        return _heliocentric_view(
            start_time = self.start_time,
            end_time = self.end_time,
            conditions = conditions,
            filters = filters,
            title = title,
            projection = projection,
            library = library,
            cache_data = cache_data,
            planets = planets,
            **orbital_elements
        )   
    
    def single_heliocentric_plots(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        planets: Optional[bool] = False,
        **orbital_elements
    ):
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_view(filters = [_filter], cache_data = cache_data, planets = planets, **orbital_elements))
    
        return plots
    
    def heliocentric_histogram(
        self,
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        planets: Optional[bool] = False,
        **orbital_elements
    ):
        
        conditions = []
        
        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        
        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = True, **orbital_elements)
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        return _heliocentric_histogram(
            start_time = self.start_time,
            end_time = self.end_time,
            conditions = conditions,
            filters = filters,
            title = title,
            library = library,
            cache_data = cache_data,
            planets = planets,
            **orbital_elements
        )
    
    def single_heliocentric_histogram(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        planets: Optional[bool] = False,
        **orbital_elements
    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_histogram(filters = [_filter], cache_data = cache_data, planets = planets, **orbital_elements))
    
        return plots
        
    def heliocentric_hexplot(
        self,     
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        planets: Optional[bool] = False,
        **orbital_elements
    ):

        conditions = []
        
        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        
        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = True, **orbital_elements)
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)
            

        return _heliocentric_hexplot(
            start_time = self.start_time,
            end_time = self.end_time,
            conditions = conditions,
            filters = filters,
            title = title,
            library = library,
            cache_data = cache_data,
            planets = planets,
            **orbital_elements
        )  
        
    def single_heliocentric_hexplot(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        min_hd: Optional[float] = None,
        max_hd: Optional[float] = None,
        planets: Optional[bool] = False,
        **orbital_elements
    ):
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
            
        plots = []

        for _filter in filters:
            plots.append(self.heliocentric_hexplot(filters = [_filter], cache_data = cache_data, planets = planets, title = f"{_filter} Filter", **orbital_elements))
        
        return plots
    
    def topocentric_view(
        self,   
        filters: Optional[list] = None,
        title : Optional[str] = None,
        projection: Optional[Literal['2d', '3d']] = '2d',
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        conditions = []
        
        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        
        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = True, **orbital_elements)
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        return _topocentric_view(
            start_time = self.start_time,
            end_time = self.end_time,
            conditions = conditions,
            filters = filters,
            title = title,
            library = library,
            cache_data = cache_data,
            **orbital_elements
        )  
    
    def single_topocentric_plots(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
       **orbital_elements
    ):
        
           
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            plots.append(self.topocentric_view(filters = [_filter], cache_data = cache_data, title = f"{_filter} Filter", **orbital_elements))
            
        return plots
    
    def topocentric_histogram(
        self,
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        conditions = []
        
        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        
        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = True, **orbital_elements)
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)
            

        return _topocentric_histogram(
            start_time = self.start_time,
            end_time = self.end_time,
            conditions = conditions,
            filters = filters,
            title = title,
            library = library,
            cache_data = cache_data,
            **orbital_elements
        )  
    def single_topocentric_histogram(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
               
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            plots.append(self.topocentric_histogram(filters = [_filter], cache_data = cache_data, title = f"{_filter} Filter", **orbital_elements))
            
    def topocentric_hexplot(
        self,
        filters: Optional[list] = None,
        title : Optional[str] = None,
        marginals: Optional[bool] = True,
        library: Optional[str] =  "seaborn",
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):
        conditions = []
        
        filters, conditions = self.filter_conditions(filters = filters, conditions = conditions)
        
        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = True, **orbital_elements)
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)

        return _heliocentric_hexplot(
            start_time = self.start_time,
            end_time = self.end_time,
            conditions = conditions,
            filters = filters,
            title = title,
            library = library,
            cache_data = cache_data,
            **orbital_elements
        )  

    
    def single_topocentric_hexplot(
        self,
        filters: Optional[list] = None,
        cache_data: Optional[bool] = False,
        **orbital_elements
    ):           
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        if filters == None:
            filters = ["g", "r", "i", "z", "y", "u"]
        
        plots = []
        
        for _filter in filters:
            try:
                plots.append(self.topocentric_hexplot(filters = [_filter], cache_data = cache_data, title = f"{_filter} Filter", **orbital_elements))
            except:
                print(f"Unable to add {_filter} filter to plots")
    
    def orbital_relations(   
        self,
        x : Literal["incl", "q", "e", "a"],
        y : Literal["incl", "q", "e", "a"],
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        title : Optional[str] = None,
        plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
        cache_data: Optional[bool] = False,
        marginals: Optional[bool] = True,
        **orbital_elements
    ):
        

        conditions = []
        
        if self.start_time:
            conditions.append(diasource.c['midpointtai'] >= self.start_time)

        if self.end_time:
            conditions.append(diasource.c['midpointtai'] <= self.end_time)
        
        orbital_elements, conditions = self.orbital_conditions(conditions = conditions, helio = False, **orbital_elements)
        

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
                mpcorb, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']
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
        if timeframe not in TIMEFRAME:
            raise Exception(f"Timeframe must be one of {TIMEFRAME}")


        conditions = create_orbit_conditions(conditions = [], **orbital_elements)

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

        return hp
    
    
    def daily_detection_distributions(
        self,
        DistanceMinMax=[[0,2],[2,6],[6,25],[25,100]]
):
        return _daily_detection_distributions(
            start_time = self.start_time,
            end_time = self.end_time,
            DistanceMinMax = DistanceMinMax
        )
        
    
    @staticmethod
    def population_detection_distributions(
        # split into populations
        start_time : Optional[float] = None, end_time : Optional[float] = None,
        title : Optional[str] = None,
        timeframe : Literal["daily", "monthly", "yearly"] = "daily",
        time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
        cache_data: Optional[bool] = False,
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
        position: Optional[list] = None,
        **orbital_elements
    ):
        parameter = parameter.lower()
        
        if parameter not in ["e", "incl", "q", "a"]:
            raise Exception(f"Orbital parameter must be one of: e, incl, q, a")
        orbital_elements = self.merge_orbital_arguments(**orbital_elements)    
        if 'min_hd' in orbital_elements:
            orbital_elements.pop("min_hd")
        
        if 'max_hd' in orbital_elements:
            orbital_elements.pop("max_hd")
        
        filters, _ = self.filter_conditions(filters = filters, conditions = [])
        
        args = dict(
            filters = filters,
            plot_type = plot_type,
            start_time = self.start_time,
            end_time = self.end_time,
            cache_data = cache_data,
            title = title,
            position = position,
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
        pretty_format: Optional[list] = None,
        **orbital_elements
    ):
        
        if pretty_format is not None and pretty_format not in [[2,2],  [4,1], [1,4]]:
            raise Exception(f"Invalid pretty format for this function. Available formats are : {[2,2],  [4,1], [1,4]}")
            
        if pretty_format == [2,2]:
            positions = [['0','0'], ['0','1'], ['1','0'], ['1','1']]
        if pretty_format == [4, 1]:
            positions = [['0','0'], ['0','1'], ['0','2'], ['0','3']]
        if pretty_format == [1,4]:
            positions = [['0','0'], ['1','0'], ['2','0'], ['3','0']]
            
        plots = []
            
        for i, element in enumerate(["e", "incl", "q", "a"]):
            args = dict(
                filters = filters,
                plot_type = plot_type,
                cache_data = cache_data,
                title = title,
                **orbital_elements
            )
        
                         
            if pretty_format:
                args['position'] = positions[i]

            plots.append(
                self.orbital_distributions(
                    parameter = element,
                    **args
                )
            )
                         
        if pretty_format:
            pretty_plt =  MultiPlot(dimensions = pretty_format)
            pretty_plt.add(
                plots
            )
            if pretty_format == [1, 4] or pretty_format == [4,1]:
                pretty_plt.fig.set_figwidth(16)
            
            return pretty_plt
                             
        else:
            return plots


    
