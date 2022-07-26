from database import db
from database.validators import validate_orbital_elements, validate_times, validate_filters
from database.schemas import sssource, mpcorb, diasource
from database.conditions import create_orbit_conditions

from orbital_element_distributions import _orbital_relations, eccentricity, perihelion, semi_major_axis, inclination, _tisserand_relations
#change to relations


from objects_in_field import objects_in_field

from observations import _detection_distributions

from typing import Optional, Literal

from sqlalchemy import select, func, distinct, column

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

            'q' : mpcorb.c['q'],
            'e' : mpcorb.c['e'],
            'incl' : mpcorb.c['incl'],
            'a': (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a'),

            'tisserand' : tisserand
        }
        
        self.data = None

        if lazy_loading == False:
            #load data now.
            self.data = self.get_data(list(self.table_columns.keys()))
    
    def get_data(self, cols):
        # THIS DISTINCT WORKS
        
        df = db.query(
                    select(
                        *[self.table_columns[col] for col in cols]
                    ).join(
                        diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']
                    ).join(
                        sssource, sssource.c['ssobjectid'] == mpcorb.c['ssobjectid']
                    ).distinct(mpcorb.c['ssobjectid']).where(*self.conditions)
                )
        if self.data is None:
            self.data = df
        
        else:
            #print(df)
            self.data = self.data.merge(
                df,
                on = ['ssobjectid', 'midpointtai']
            )
            
        return self.data
    
    def check_data(self, cols_required):
        #print(cols_required)
        #print(self.data.columns)
        
        if self.lazy_loading:
            if self.data is None:
                df = self.get_data(cols_required) 
                
            else:
                c = ['ssobjectid', 'midpointtai']
                for col in cols_required:
                   
                    if (col in self.data.columns):
                        pass
                        # This needs cleaned up
                        
                        #cols_required = cols_required.remove(col)
                    else:
                        c.append(col)
                    
                #print(f"Required {cols_required}, {c}")
                #if cols_required:
                    # now get columns
                df = self.get_data(c)
                    #merge with existing dataframe
                        
                #df = self.data
        else:
            df = self.data #self.get_data(list(self.table_columns.keys()))
        return df
    
    def detection_distributions(self,
                                start_time : Optional[float] = None,
                                end_time : Optional[float] = None,
                                time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                                    timeframe : Literal["daily", "monthly", "year"] = "daily",

                                cache_data: Optional[bool] = False):
        # hex plots
        # fix for monthly and yearly
        
        #start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
        df = self.check_data(
            ['midpointtai', 'ssobjectid']
        )
            
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        
        return _detection_distributions(
            df = df[['midpointtai', 'ssobjectid']],
            start_time = start_time if start_time else self.start_time,
            end_time = end_time if end_time else self.end_time,
            time_format = time_format,
            cache_data = cache_data,
            timeframe = timeframe
        )
    
    #add _orbital_relations
    
    def plot_objects(self,
                    filters: Optional[list] = None,
                    title : Optional[str] = None,
                     start_time : Optional[float] = None, end_time : Optional[float] = None,
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                    projection: Optional[Literal['2d', '3d']] = '2d',
                    library: Optional[str] =  "seaborn",
                    cache_data: Optional[bool] = False
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
        
        df = self.check_data(
            ['ssobjectid', 'filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid', 'midpointtai']
        )
        
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        if filters:
            df = df.loc[df['filter'].isin(filters)].copy()
        
        
        return objects_in_field(
            df[['filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid']],
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format,
            projection = projection,
            library = library,
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
    
    def orbital_relations(self,
                         x : Literal["incl", "q", "e", "a"],
                         y : Literal["incl", "q", "e", "a"],
                         start_time : Optional[float] = None, end_time : Optional[float] = None,
                         title : Optional[str] = None,
                         colorbar: bool = True,
                         plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
                         cache_data: Optional[bool] = False
                         ):
        
        
        df = self.check_data(
            ['ssobjectid','midpointtai', x, y]
        )
            
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()

        
        return _orbital_relations(
            df = df[[x, y, 'ssobjectid', 'midpointtai']],
            x = x, 
            y = y,
            start_time = start_time if start_time else self.start_time, 
            end_time = end_time if end_time else self.end_time,
            plot_type = plot_type, title = title,
            cache_data = cache_data,
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
                            cache_data: Optional[bool] = False
                           ):
        
        df = self.check_data(
            ['ssobjectid', 'midpointtai', 'tisserand', y]
        )
        
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        
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

    def orbital_param_distribution(self,
                                    parameter : Literal[ORB_PARAMS],
                                    filters: Optional[list] = None,
                                    start_time : Optional[float] = None, 
                                    end_time : Optional[float] = None,
                                    plot_type: Literal[PLOT_TYPES] = 'BOX',
                                    title : Optional[str] = None,
                                    library: Optional[str] = "seaborn",
                                    cache_data: Optional[bool] = False
                                  ):
        
        parameter = parameter.lower()
        
        if parameter not in ORB_PARAMS:
            raise Exception(f"Orbital parameter must be one of: {ORB_PARAMS}")
        
        required_cols = ['ssobjectid', 'midpointtai', 'filter']
        
        if parameter == "eccentricity":
            required_cols.append("e")
        if parameter == "semi_major_axis":
            required_cols.append("a")
        if parameter == "inclination":
            required_cols.append("incl")
        if parameter == "perihelion":
            required_cols.append("q")
            
        df = self.check_data(
            required_cols
        )
        
        
        #if start_time:
        #if end_time:
        if self.start_time:
            df = df.loc[df['midpointtai'] >= self.start_time].copy()
        
        if self.end_time:
            df = df.loc[df['midpointtai'] <= self.end_time].copy()
            
        if filters:
            df = df.loc[df['filter'].isin(filters)].copy()
            
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
        
        if parameter == "eccentricity":
            return eccentricity(
                df[['filter', 'e', 'ssobjectid']],
                **args
            )
        if parameter == "inclination":
            return inclination(
                df[['filter', 'incl', 'ssobjectid']], 
                **args
            )
        if parameter == "semi_major_axis":
            return semi_major_axis(
                df[['filter', 'a', 'ssobjectid']], 
                **args
            )
        if parameter == "perihelion":
            return perihelion(
                df[['filter', 'q', 'ssobjectid']], 
                **args
            )
        
        #getter setter for __init__ that calls functions and updates plots
        
    def clear(self):
        #clear all the dataframes
        self.data = None
        return
        
    