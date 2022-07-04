from plots.box import BoxPlot, BoxenPlot
from plots.violin import ViolinPlot
from plots.symbols import DEGREE

from database import db
from database.schemas import DIASource, diasource, mpcorb
from database.validators import validate_times, validate_filters,\
    validate_perihelion, validate_inclination, validate_semi_major_axis
from database.format_time import format_times

import seaborn as sns
import matplotlib.pyplot as plt

from typing import Optional, Literal

from sqlalchemy import select, func


PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']

ELEMENTS = {'e' : {'label': 'Eccentricity','unit' : None},\
            'a' : {'label': 'Semi-Major axis', 'unit': 'au'},\
            'peri' : {'label': 'Perihelion', 'unit': 'au'}, \
            'incl' : {'label' : 'Inclination', 'unit' : DEGREE}
           }

def base(
         stmt,
         element, # e, incl, a, peri
         filters: Optional[list] = None,
         min_e: float = 0, max_e : float = None,
         min_peri: float = 0.0, max_peri : float = None,
         min_a: float = 0.0, max_a : float = None,
         min_incl: float = 0.0, max_incl: float = None,
         start_time : Optional[float] = None, end_time : Optional[float] = None,
         plot_type: Literal[PLOT_TYPES] = 'BOX',
         title : Optional[str] = None,
        ):
    
    plot_type = plot_type.upper()

    if plot_type not in PLOT_TYPES:
        raise TypeError(f"{plot_type} is not a valid chart option. Valid plot options include 'BOX', 'BOXEN' or 'VIOLIN'")
    
    conditions = []
    
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    
    # need a validate eccentricty function
    
    if start_time:
        conditions.append(diasource.c['midpointtai'] >= start_time)
    
    if end_time:
        conditions.append(diasource.c['midpointtai'] <= end_time)
    
    if filters:
        filters = validate_filters(list(set(filters)))
        conditions.append(diasource.c['filter'].in_(filters))
        
    min_peri, max_peri = validate_perihelion(min_peri, max_peri)
    min_incl, max_incl = validate_inclination(min_incl = min_incl, max_incl = max_incl)
    min_a, max_a = validate_semi_major_axis(min_a, max_a)
   
    
    
    if min_peri:
        conditions.append(mpcorb.c['peri'] >= min_peri)
    if max_peri:
        conditions.append(mpcorb.c['peri'] <= max_peri)
    
    
        
    if min_incl:
        conditions.append(mpcorb.c['incl'] >= min_incl)
    
    if max_incl:
        conditions.append(mpcorb.c['incl'] <= max_incl)
        
    if min_a or max_a:
        conditions.append(mpcorb.c['e'] > 0 )
    
        conditions.append(mpcorb.c['e'] < 1)
    
    elif not min_a and not max_a:
        if min_e:
            conditions.append(mpcorb.c['e'] >= min_e )
        if max_e:
            conditions.append(mpcorb.c['e'] <= min_e )
                
    if min_a:
        conditions.append((mpcorb.c['peri'] / (1 - mpcorb.c['e']) ) >= min_a)
    
    if max_a:
        conditions.append((mpcorb.c['peri'] / (1 - mpcorb.c['e']) ) <= max_a)
        
        
    df = db.query(
        stmt.where(
            *conditions
        ) 
   )
    if df.empty:
        query = f"""No results returned for your query:\n"""
        if filters:
            query += f"filters : {filters}\n"
        if start_time:
            query += f"start_time : {start_time}\n"
        if end_time:
            query += f"end_time : {end_time}\n"
        if min_e:
            query += f"min_e : {min_e}\n"
        if max_e:
            query += f"max_e : {max_e}\n"
        if min_a:
            query += f"min_a : {min_a}\n"
        if max_a:
            query += f"max_a : {max_a}\n"
        if min_incl:
            query += f"min_incl : {min_incl}\n"
        if max_incl:
            query += f"max_incl : {max_incl}\n"
        if min_peri:
            query += f"min_peri : {min_peri}\n"
        if max_peri:
            query += f"max_peri : {max_peri}\n"
        
        query = query[0:-1]
                         
        raise Exception(query)

    '''
    # TODO add plot info card
    if start_time:
        plot_info['start'] = start_time
    
    if end_time:
        plot_info['end'] = end_time
    
    if min_a:
        plot_info['min_a'] = min_a
    
    '''
    start_time, end_time = format_times([start_time, end_time], _format="ISO")
    label = ELEMENTS[element]['label']
    unit = ELEMENTS[element]['unit']
    xlabel = label
    if unit:
        xlabel += f' ({unit})'
    args = dict(data = df, x = element, 
                xlabel = f'{xlabel}', 
               ) # plot_info = plot_info
    
    if filters:
        args['y'] = "filter"
        args['ylabel'] = "Filter"
        filters_str = ", ".join(filters) if len(filters) > 1 else filters[0]
        
        if title:
            args['title']= title
        else:
            args['title'] =f"{label} distributions across filters ({filters_str})\n {start_time} - {end_time}"
    else:
        
        if title:
            args['title']= title 
        else:
            args['title'] = f"{label} distributions across all filters\n {start_time}-{end_time}"    
    
    if plot_type == "BOX":
        return BoxPlot(**args)
    elif plot_type == "VIOLIN":
        return ViolinPlot(**args)
    else:
        return BoxenPlot(**args)
    
def eccentricity(filters: Optional[list] = None,
                 min_e: float = None, max_e : float = None,
                 min_peri: float = 0.0, max_peri : float = None,
                 min_a: float = 0.0, max_a : float = None,
                 min_incl: float = 0.0, max_incl: float = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX',
                 title : Optional[str] = None
                ):
    
    """   
    """
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        min_e = min_e, max_e = max_e,
        min_a = min_a, max_a = max_a,
        min_peri = min_peri, max_peri = max_peri,
        min_incl = min_incl, max_incl = max_incl,
        plot_type = plot_type,
        title = title,
        element = 'e',
        stmt = select(
            func.distinct(mpcorb.c['ssobjectid']), mpcorb.c['e'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )
        
    
def perihelion(filters: Optional[list] = None,
                 min_e: float = 0, max_e : float = None,
                 min_peri: float = 0.0, max_peri : float = None,
                 min_a: float = 0.0, max_a : float = None,
                 min_incl: float = 0.0, max_incl: float = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX',
                 title : Optional[str] = None,
                  ):
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        min_e = min_e, max_e = max_e,
        min_a = min_a, max_a = max_a,
        min_peri = min_peri, max_peri = max_peri,
        min_incl = min_incl, max_incl = max_incl,
        plot_type = plot_type,
        title = title,
        element = 'peri',
        stmt = select(func.distinct(mpcorb.c['ssobjectid']), mpcorb.c['peri'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )
        
    
def inclination(filters: Optional[list] = None,
                 min_e: float = 0, max_e : float = None,
                 min_peri: float = 0.0, max_peri : float = None,
                 min_a: float = 0.0, max_a : float = None,
                 min_incl: float = 0.0, max_incl: float = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX',
                 title : Optional[str] = None):
    
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        min_e = min_e, max_e = max_e,
        min_a = min_a, max_a = max_a,
        min_peri = min_peri, max_peri = max_peri,
        min_incl = min_incl, max_incl = max_incl,
        plot_type = plot_type,
        title = title,
        element = 'incl',
        stmt = select(func.distinct(mpcorb.c['ssobjectid']),mpcorb.c['incl'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )

    
        
def semi_major_axis(filters: Optional[list] = None,
                 min_e: float = None, max_e : float = None,
                 min_peri: float = 0.0, max_peri : float = None,
                 min_a: float = 0.0, max_a : float = None,
                 min_incl: float = 0.0, max_incl: float = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX',
                 title : Optional[str] = None
                ):
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        min_e = min_e, max_e = max_e,
        min_a = min_a, max_a = max_a,
        min_peri = min_peri, max_peri = max_peri,
        min_incl = min_incl, max_incl = max_incl,
        plot_type = plot_type,
        title = title,
        element = 'a',
        stmt = select(func.distinct(mpcorb.c['ssobjectid']).label('ssobjectid'), mpcorb.c['peri'], (mpcorb.c['peri'] / (1 - mpcorb.c['e'])).label('a') , diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )

    