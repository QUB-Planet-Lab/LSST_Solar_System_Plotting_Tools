from .format_time import format_times


FILTERS = ["g", "r", "i", "z", "y", "u"]
def validate_times(start_time = None, end_time = None):

    
    if start_time:
        start_time = format_times(times = [start_time], _format="MJD")[0]
    if end_time:
        end_time = format_times(times = [end_time], _format="MJD")[0]
   
    if (start_time and end_time) and (start_time > end_time):
        raise Exception("Invalid time range. The start_time must be greater than the end_time to create a valid range")
    
    return start_time, end_time

def validate_filter(_filter: str):
    if _filter not in FILTERS:
        raise TypeError(f"Please specifiy a filter from one of the following: {FILTERS}")
    return _filter

def validate_filters(filters : list):
    if type(filters) != list:
        raise TypeError(f"Please specifiy a list that may include the following: {FILTERS}")
    for _filter in filters:
        if _filter not in FILTERS:
            raise Exception(f"{_filter} is not a valid filter. Please specifiy a list that may include the following: {FILTERS}")
    return filters

def validate_perihelion(min_peri: float, max_peri: float):
    if (min_peri and (type(min_peri) != float or min_peri < 0)) or (max_peri and (type(min_peri) != float or max_peri < 0)):
        raise Exception(f"""Perihelion distances specified by min_peri and max_peri must assume positive float values or None.
        
        Input specified: min_peri = {min_peri}, max_peri = {max_peri}""")
        
    return min_peri, max_peri

def validate_inclination(min_incl: float = None, max_incl:float = None):
    if (min_incl and min_incl < 0) or (max_incl and max_incl  < 0):
        raise Exception(f"max_incl and min_incl must be greater than 0 degrees and less than 180 degrees")
    
    if (min_incl and min_incl > 180) or (max_incl and max_incl > 180):
        raise Exception(f"max_incl and min_incl must be greater than 0 degrees and less than 180 degrees")
        
    if (min_incl and max_incl) and (min_incl > max_incl):
        raise Exception(f"max_incl must be greater than min_incl")
    
    return min_incl, max_incl
        
    
def validate_semi_major_axis(min_a : float = None, max_a:float = None):
    if (min_a and min_a < 0) or (max_a and max_a < 0):
        raise Exception("min_a and max_a must be greater than 0")
    if (min_a and max_a) and min_a > max_a:
        raise Exception("max_a must be greater than min_a")
        
    return min_a, max_a


elements = ['min_a', 'max_a', 'min_e', 'max_e', 'min_peri', 'max_peri', 'min_incl', 'max_incl']

def validate_orbital_elements(**kwargs):
    for kwarg in kwargs:
        if kwarg not in elements:
            raise Exception(f"{kwarg} not a valid orbital_element argument. Valid arguments include {elements}")
    min_a, max_a = validate_semi_major_axis(
        min_a = kwargs['min_a'] if 'min_a' in kwargs else None, 
        max_a = kwargs['max_a'] if 'max_a' in kwargs else None
    )    
    min_incl, max_incl = validate_inclination(
        min_incl = kwargs['min_incl'] if 'min_incl' in kwargs else None, 
        max_incl = kwargs['max_incl'] if 'max_incl' in kwargs else None
    )
    min_peri, max_peri = validate_perihelion(
        min_peri = kwargs['min_peri'] if 'min_peri' in kwargs else None,
        max_peri = kwargs['max_peri'] if 'max_peri' in kwargs else None
    )
    min_e, max_e = kwargs['min_e'] if 'min_e' in kwargs else None, kwargs['max_e'] if 'max_e' in kwargs else None
    
    return min_a, max_a, min_incl, max_incl, min_peri, max_peri, min_e, max_e
