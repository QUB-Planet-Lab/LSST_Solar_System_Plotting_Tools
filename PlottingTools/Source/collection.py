from database import db
from database.validators import validate_orbital_elements, validate_times, validate_filters
from database.schemas import sssource, mpcorb, diasource
from database.conditions import create_orbit_conditions

from orbital_element_distributions import _orbital_relations, eccentricity, perihelion, semi_major_axis, inclination, _tisserand_relations
#change to relations


from objects_in_field import objects_in_field

from observations import _detection_distributions

from typing import Optional, Literal

from sqlalchemy import select, func, distinct

PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']
ORB_PARAMS = ["eccentricity", "perihelion", "semi_major_axis", "inclination"]

class Collection():
    def __init__(self, lazy_loading: Optional[bool] = True, start_time : Optional[float] = None, end_time : Optional[float] = None, **orbital_elements):
        
        
        
        self.lazy_loading = lazy_loading
        
        self.min_a, self.max_a, self.min_incl, self.max_incl, self.min_peri, self.max_peri, self.min_e, self.max_e = validate_orbital_elements(**orbital_elements)
        
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

            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],

            mpcorb.c['q'],
            mpcorb.c['e'],
            mpcorb.c['incl'],
            (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a'),

            tisserand
        ]
    
        if lazy_loading == False:
            #load data now.
            self.data = self.get_data()
    
        else:
            self.data = None
        
        
    def get_data(self):
        # THIS DISTINCT WORKS
        
        self.data = db.query(
                select(
                    *self.cols
                ).join(
                    diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']
                ).join(
                    sssource, sssource.c['ssobjectid'] == mpcorb.c['ssobjectid']
                ).distinct(mpcorb.c['ssobjectid']).where(*self.conditions)
            )
        return self.data
    
    def check_data(self):
        if self.lazy_loading:
            if self.data is None:
                df = self.get_data() #provide only necessary columns
            else:
                df = self.data
        else:
            df = self.get_data()
        return df
    
    
    def detection_distributions(self, start_time : Optional[float] = None, end_time : Optional[float] = None,
    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO'):
        # hex plots
        # fix for monthly and yearly
        
        #start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
        df = self.check_data()
            
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        
        return _detection_distributions(
            df = df,
            start_time = start_time if start_time else self.start_time,
            end_time = end_time if end_time else self.end_time,
            time_format = time_format,
        )
    
    #add _orbital_relations
    
    def plot_objects(self,
                    filters: Optional[list] = None,
                    title : Optional[str] = None,
                     start_time : Optional[float] = None, end_time : Optional[float] = None,
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                    projection: Optional[Literal['2d', '3d']] = '2d',
                    library: Optional[str] =  "seaborn"
                    ): 
        # plot orbits of all items. Nice to animate in the future
        #objects_in_field
        
        '''
        currently specifying start and end, could have additional as long as they are in the range from the dataframe or make a new call.
        
        start_time, end_time = validate_times(
            start_time = start_time if start_time else self.start_time,
            end_time = end_time if end_time else self.end_time,
        )
        '''
        
        df = self.check_data()
        
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        if filters:
            df = df.loc[df['filter'].isin(filters)].copy()
        
        df = self.check_data()
        
        
        return objects_in_field(
            df,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format,
            projection = projection,
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
    
    def orbital_relations(self,
                         x : Literal["incl", "q", "e", "a"],
                         y : Literal["incl", "q", "e", "a"],
                         start_time : Optional[float] = None, end_time : Optional[float] = None,
                         title : Optional[str] = None,
                         colorbar: bool = True,
                         plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter"
                         ):
        
        
        df = self.check_data()
            
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        return _orbital_relations(
            df = df,
            x = x, 
            y = y,
            start_time = start_time if start_time else self.start_time, 
            end_time = end_time if end_time else self.end_time,
            plot_type = plot_type, title = title,
            min_a = self.min_a, max_a = self.max_a, 
            min_incl = self.min_incl, max_incl = self.max_incl, 
            min_peri = self.min_peri, max_peri = self.max_peri, 
            min_e = self.min_e, max_e = self.max_e
       )
                           
    
    def tisserand_relations(self,
                            y : Literal["incl", "q", "e", "a"],
                            start_time : Optional[float] = None, end_time : Optional[float] = None,
                            title : Optional[str] = None,
                            plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
                           ):
        
        df = self.check_data()
        
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        
        tr = _tisserand_relations(
            df = df,
            y = y,  
            #start_time = start_time if start_time else self.start_time, 
            #end_time = end_time if end_time else self.end_time, 
            title = title, plot_type = plot_type, min_a = self.min_a, 
            max_a = self.max_a,
            min_incl = self.min_incl,
            max_incl = self.max_incl,
            min_peri = self.min_peri, 
            max_peri = self.max_peri, 
            min_e = self.min_e, 
            max_e = self.max_e
       )
        
        tr.ax.set_xlim(left = tr.data["tisserand"].min(), right = tr.data["tisserand"].max())
        tr.ax.set_ylim(bottom =  tr.data[y].min(), top = tr.data[y].max())
        
        return tr

    def orbital_param_distribution(self,
                                    parameter : Literal[ORB_PARAMS],
                                    filters: Optional[list] = None,
                                    start_time : Optional[float] = None, 
                                    end_time : Optional[float] = None,
                                    plot_type: Literal[PLOT_TYPES] = 'BOX',
                                    title : Optional[str] = None,
                                   library: Optional[str] = "seaborn"
                                  ):
        
        parameter = parameter.lower()
        
        if parameter not in ORB_PARAMS:
            raise Exception(f"Orbital parameter must be one of: {ORB_PARAMS}")
        
        
        df = self.check_data()
        
        
        #if start_time:
        #if end_time:
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        if filters:
            df = df.loc[df['filter'].isin(filters)].copy()
            
        args = dict(
            df = df,
            filters = filters,
            plot_type = plot_type,
            #start_time = start_time if start_time else self.start_time,
            #end_time = end_time if end_time else self.end_time,
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
        
        if parameter == "eccentricity":
            return eccentricity(
                **args
            )
        if parameter == "inclination":
            return inclination(
                **args
            )
        if parameter == "semi_major_axis":
            return semi_major_axis(
                **args
            )
        if parameter == "perihelion":
            return perihelion(
                **args
            )
        
        #getter setter for __init__ that calls functions and updates plots
        
    def clear(self):
        #clear all the dataframes
        self.data = None
        return
        
    