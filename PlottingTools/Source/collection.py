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




class Objects():
    def __init__(self, start_time , end_time, lazy_loading: Optional[bool] = True,  **orbital_elements):

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
        

        if lazy_loading == False:
            self.data = self.get_data(list(self.table_columns.keys()))
        else:
            self.data = None
            
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
    
    
    def plot_objects(self,
                    filters: Optional[list] = None,
                    title : Optional[str] = None,
                     
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                    projection: Optional[Literal['2d', '3d']] = '2d',
                    library: Optional[str] =  "seaborn",
                    cache_data: Optional[bool] = False
                    ): 
        
        df = self.check_data(
            ['ssobjectid', 'filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid', 'midpointtai']
        )
     
           
        return objects_in_field(
            df[['filter', 'heliocentricx', 'heliocentricy', 'heliocentricz', 'ssobjectid']],
            filters = filters,
            start_time = self.start_time,
            end_time = self.end_time,
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
        
    