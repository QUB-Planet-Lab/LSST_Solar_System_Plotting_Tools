from database import db
from database.validators import validate_orbital_elements, validate_times

from orbital_element_distributions import _orbital_relations, eccentricity, perihelion, semi_major_axis, inclination, _tisserand_relations
#change to relations

from objects_in_field import objects_in_field

from observations import _detection_distributions

from typing import Optional, Literal


PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']
ORB_PARAMS = ["eccentricity", "perihelion", "semi_major_axis", "inclination"]

class Collection():
    def __init__(self, start_time : Optional[float] = None, end_time : Optional[float] = None, **orbital_elements):
        
        self.min_a, self.max_a, self.min_incl, self.max_incl, self.min_peri, self.max_peri, self.min_e, self.max_e = validate_orbital_elements(**orbital_elements)
        
        self.start_time, self.end_time = validate_times(start_time = start_time, end_time = end_time)
        
        
    def detection_distributions(self, start_time : Optional[float] = None, end_time : Optional[float] = None,
    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',):
        # hex plots
        # fix for monthly and yearly

        return _detection_distributions(
            start_time = start_time if start_time else self.start_time,
            end_time = end_time if end_time else self.end_time,
            time_format = time_format,
            min_a = self.min_a, 
            max_a = self.max_a,
            min_incl = self.min_incl,
            max_incl = self.max_incl,
            min_peri = self.min_peri, 
            max_peri = self.max_peri, 
            min_e = self.min_e, 
            max_e = self.max_e
        )
    
    #add _orbital_relations
    
    def plot_objects(self,
                    filters: Optional[list] = None,
                    title : Optional[str] = None,
                     start_time : Optional[float] = None, end_time : Optional[float] = None,
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                    projection: Optional[Literal['2d', '3d']] = '2d',
                    ): 
        # plot orbits of all items. Nice to animate in the future
        #objects_in_field
        
        return objects_in_field(
            filters = filters,
            start_time = start_time if start_time else self.start_time,
            end_time = end_time if end_time else self.end_time,
            title = title,
            time_format = time_format,
            projection = projection,
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
        
        return _orbital_relations(x = x, y = y, 
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
        tr = _tisserand_relations(y = y,  
                                  
                                  start_time = start_time if start_time else self.start_time, 
                                  end_time = end_time if end_time else self.end_time, 
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
                                  ):
        
        parameter = parameter.lower()
        
        if parameter not in ORB_PARAMS:
            raise Exception(f"Orbital parameter must be one of: {ORB_PARAMS}")
        
        args = dict(
            filters = filters,
            plot_type = plot_type,
            start_time = start_time if start_time else self.start_time,
            end_time = end_time if end_time else self.end_time,
            title = title,
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
        if parameter == "semi-major-axis":
            return semi_major_axis(
                **args
            )
        if parameter == "perihelion":
            return perihelion(
                **args
            )
        
        #getter setter for __init__ that calls functions and updates plots
    
    