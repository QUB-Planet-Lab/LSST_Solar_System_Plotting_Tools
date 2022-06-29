from DataAccessLayer import create_connection_and_queryDB
from plots.box import BoxPlot, BoxenPlot
from plots.violin import ViolinPlot
from plots.symbols import DEGREE

import seaborn as sns
import matplotlib.pyplot as plt

from database import db
from sqlalchemy import select, func
from sqlalchemy import func
from database.schemas import DIASource, diasource, mpcorb
from database.validators import validate_times, validate_filters, validate_perihelion, validate_inclination

from typing import Optional, Literal


PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']

def eccentricity(filters: Optional[list] = None,
                 min_e: float = 0, max_e : float = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX'):
    
    """ eccentricity() returns a BoxenPlot object
    
    """

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
    print(filters)
    df = db.query(
        select( mpcorb.c['e'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).where(
                *conditions
        ).distinct() 
        .limit(1000)
    )
    if df.empty:
        raise Exception(f"""No results returned for your query: 
                    
                    filters: {filters},
                    start_time: {start_time},
                    end_time: {end_time},
                    min_e: {e},
                    max_peri: {max_e},
                """)
    
    if filters:
        filters_str = ", ".join(filters) if len(filters) > 1 else filters[0]
        
        args = dict(data = df, x="e", y="filter", title=f"Eccentricity distributions across filters ({filters_str}) from {start_time} - {end_time}", xlabel="Perihelion (au)", ylabel="Filters",rc_params={'figure.figsize':(12,8)})
        
        if plot_type == "BOX":
            return BoxPlot(**args)
        elif plot_type == "VIOLIN":
            return ViolinPlot(**args)
        else:
            return BoxenPlot(**args)
    
    else:
        args = dict(data = df, x = "e", xlabel = "Eccentricity", title=f"Eccentricity distributions across all filters {start_time}-{end_time}", rc_params={'figure.figsize':(12,8)})
        if plot_type == "BOX":
            return BoxPlot(**args)
        elif plot_type == "VIOLIN":
            return ViolinPlot(**args)
        else:
            return BoxenPlot(**args)    
    
def perihelion(filters: Optional[list] = None,
               min_peri: float = 0, max_peri : float = None,
               start_time : Optional[float] = None, end_time : Optional[float] = None,
               plot_type: Literal[PLOT_TYPES] = 'BOX'):
    
    plot_type = plot_type.upper()

        
    if plot_type not in PLOT_TYPES:
        raise TypeError(f"{plot_type} is not a valid chart option. Valid plot options include 'BOX', 'BOXEN' or 'VIOLIN'")
    
    conditions = []
    
    min_peri, max_peri = validate_perihelion(min_peri, max_peri)
    
    if max_peri:
        conditions.append(mpcorb.c['peri'] < max_peri)
    if min_peri:
        conditions.append(mpcorb.c['peri'] > min_peri)
    
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    
    if start_time:
        conditions.append(diasource.c['midpointtai'] >= start_time)
    
    if end_time:
        conditions.append(diasource.c['midpointtai'] <= end_time)
    
    if filters:
        filters = validate_filters(list(set(filters)))
      
        conditions.append(diasource.c['filter'].in_(filters))
    
    df = db.query(
        select( mpcorb.c['peri'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).where(
                *conditions
        ).distinct()
        .limit(10000)
    )
    
    if df.empty:
        raise Exception(f"""No results returned for your query: 
                    
                    filters: {filters},
                    start_time: {start_time},
                    end_time: {end_time},
                    min_peri: {min_peri},
                    max_peri: {max_peri},
                    
                """)
        
        
    if filters:
        filters_str = ", ".join(filters) if len(filters) > 1 else filters[0]
        
        args = dict(data = df, x="peri", y="filter", title=f"Perihelion distributions across filters ({filters_str}) from {start_time} - {end_time}", xlabel="Perihelion (au)", ylabel="Filters",rc_params={'figure.figsize':(12,8)})
        
        if plot_type == "BOX":
            return BoxPlot(**args)
        elif plot_type == "VIOLIN":
            return ViolinPlot(**args)
        else:
            return BoxenPlot(**args)
    
    else:
        args = dict(data = df, x = "peri", xlabel = "Perihelion (au)", title=f"Perihelion distributions across all filters {start_time}-{end_time}", rc_params={'figure.figsize':(12,8)})
        if plot_type == "BOX":
            return BoxPlot(**args)
        elif plot_type == "VIOLIN":
            return ViolinPlot(**args)
        else:
            return BoxenPlot(**args)

def calculate_sm_axis(peri, e):
    return peri * (1 - e)

def semi_major_axis():
    #todo
    return


def inclination(filters: Optional[list] = None,
               min_incl: float = 0, max_incl : float = None,
               start_time : Optional[float] = None, end_time : Optional[float] = None,
               plot_type: Literal[PLOT_TYPES] = 'BOX'):
    
    plot_type = plot_type.upper()

    if plot_type not in PLOT_TYPES:
        raise TypeError(f"{plot_type} is not a valid chart option. Valid plot options include 'BOX', 'BOXEN' or 'VIOLIN'")
    
    conditions = []
    
    if filters:
        filters = validate_filters(list(set(filters)))
      
        conditions.append(diasource.c['filter'].in_(filters))
        
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    min_incl, max_incl = validate_inclination(min_incl = min_incl, max_incl = max_incl)
    
    if start_time:
        conditions.append(diasource.c['midpointtai'] >= start_time)
    
    if end_time:
        conditions.append(diasource.c['midpointtai'] <= end_time)
        
    
    if min_incl:
        conditions.append(mpcorb.c['incl'] >= min_incl)
    
    if max_incl:
        conditions.append(mpcorb.c['incl'] <= max_incl)
    

    df = db.query(
        select(mpcorb.c['incl'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).where(
                *conditions
        ).distinct().limit(10)
    )
    
    if df.empty:
        raise Exception(f"""No results returned for your query: 
                    
                    filters: {filters},
                    start_time: {start_time},
                    end_time: {end_time},
                    min_incl: {min_incl},
                    max_incl: {max_incl},
                    
                """)
        
        
    if filters:
        filters_str = ", ".join(filters) if len(filters) > 1 else filters[0]
        
        args = dict(data = df, x="incl", y="filter", title=f"Inclination distributions across filters ({filters_str}) from {start_time} - {end_time}", xlabel=f"Inclination ({DEGREE})", ylabel="Filters",rc_params={'figure.figsize':(12,8)})
        
        if plot_type == "BOX":
            return BoxPlot(**args)
        elif plot_type == "VIOLIN":
            return ViolinPlot(**args)
        else:
            return BoxenPlot(**args)
    
    else:
        args = dict(data = df, x = "incl", xlabel = f"Inclination ({DEGREE})", title=f"Inclination distributions across all filters {start_time}-{end_time}", rc_params={'figure.figsize':(12,8)})
        if plot_type == "BOX":
            return BoxPlot(**args)
        elif plot_type == "VIOLIN":
            return ViolinPlot(**args)
        else:
            return BoxenPlot(**args)
        
        
