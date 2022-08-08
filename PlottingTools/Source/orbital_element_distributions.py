from plots.box import BoxPlot, BoxenPlot
from plots.violin import ViolinPlot
from plots.scatter import ScatterPlot
from plots.histogram import HistogramPlot, HexagonalPlot, Histogram2D
from plots.symbols import DEGREE
from plots.styles.filter_color_scheme import COLOR_SCHEME

from database import db
from database.schemas import DIASource, diasource, mpcorb, sssource
from database.validators import validate_times, validate_filters,\
    validate_perihelion, validate_inclination, validate_semi_major_axis, validate_orbital_elements
from database.format_time import format_times

from database.conditions import create_orbit_conditions
from database.empty_response import empty_response

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from typing import Optional, Literal

from sqlalchemy import select, func, distinct

from math import cos, sqrt

PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']

ELEMENTS = {'e' : {'label': 'Eccentricity','unit' : None},\
            'a' : {'label': 'Semi-Major axis', 'unit': 'au'},\
            'q' : {'label': 'Perihelion', 'unit': 'au'}, \
            'incl' : {'label' : 'Inclination', 'unit' : DEGREE}
           }

def _tisserand_relations(
    y : Literal["incl", "q", "e", "a"],
    df : Optional[pd.DataFrame] = None,
    start_time : Optional[float] = None,
    end_time : Optional[float] = None,
    title : Optional[str] = None,
    plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
    cache_data: Optional[bool] = False,
    **orbital_elements
):
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    
        conditions = []

        if start_time:
            conditions.append(diasource.c['midpointtai'] >= start_time)

        if end_time:
            conditions.append(diasource.c['midpointtai'] <= end_time)

        conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)

        if y == "a":
            qy = (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a')
        else:
            qy = mpcorb.c[y]

        a_J = 5.2038 #au

        tisserand = (a_J / (mpcorb.c['q'] / (1 - mpcorb.c['e'])) + 2 * func.cos(mpcorb.c['incl']) * func.sqrt((mpcorb.c['q'] / (1 - mpcorb.c['e'])) / a_J * (1 - func.power(mpcorb.c['e'], 2)))).label("tisserand")

        df = db.query(
            select(
                distinct(mpcorb.c['ssobjectid']), qy, tisserand,
                diasource.c['filter']).join(
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
    
    if plot_type == "scatter":
        return ScatterPlot(data = df, x="tisserand", y=y, xlabel="Tisserand parameter", ylabel= ELEMENTS[y]['label'] + f"({ELEMENTS[y]['unit']})" if ELEMENTS[y]['unit'] else '', title = title)
    
    if plot_type == "2d_hex":
        hp = HexagonalPlot(data = df, x = "tisserand", y = y, xlabel = "Tisserand parameter",  ylabel = ELEMENTS[y]['label'] + (f" ({ELEMENTS[y]['unit']})" if ELEMENTS[y]['unit'] else ''))
        
        hp.fig.suptitle(title)
        return hp
    
    if plot_type == "2d_hist":
        hp = Histogram2D(data = df, x = "tisserand", y = y, xlabel = "Tisserand parameter",  ylabel = ELEMENTS[y]['label'] + (f" ({ELEMENTS[y]['unit']})" if ELEMENTS[y]['unit'] else ''), marginals = True)
        
        hp.fig.suptitle(title)       
        return hp

def _orbital_relations(
    x : Literal["incl", "q", "e", "a"],
    y : Literal["incl", "q", "e", "a"],
    df : Optional[pd.DataFrame] = None,
    start_time : Optional[float] = None,
    end_time : Optional[float] = None,
    title : Optional[str] = None,
    colorbar: bool = True,
    plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
    cache_data: Optional[bool] = False,
    **orbital_elements
):
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
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
                distinct(mpcorb.c['ssobjectid']), qx , qy, diasource.c['filter']).join(
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
    
    xlabel = ELEMENTS[x]['label']
    if ELEMENTS[x]['unit']:
        xlabel += f" ({ELEMENTS[x]['unit']})"
        
    ylabel = ELEMENTS[y]['label']
    if ELEMENTS[y]['unit']:
        ylabel += f" ({ELEMENTS[y]['unit']})"
        
    if plot_type == "scatter":
        return ScatterPlot(data = df, x=x, y=y, xlabel = xlabel, ylabel =  ylabel, title = title if title else "")
    
    if plot_type == "2d_hex":
        
        hp = HexagonalPlot(data = df, x = x, y = y, colorbar = colorbar, xlabel = xlabel, ylabel =  ylabel, title = title if title else "")
        
        
        return hp
    
    if plot_type == "2d_hist":
        
        hp = Histogram2D(data = df,
                         x = x,
                         y = y,
                         xlabel = xlabel, 
                         ylabel = ylabel, 
                         marginals = True, 
                         title = title
                        )
        return hp
    
def base(
         #stmt,
         df,
         element, # e, incl, a, q
         filters: Optional[list] = None,
         start_time : Optional[float] = None, end_time : Optional[float] = None,
         plot_type: Literal[PLOT_TYPES] = 'BOX',
         title : Optional[str] = None,
         library: Optional[str] = "seaborn",
         cache_data: Optional[bool] = False,
         position : Optional[list] = None,
         **orbital_elements
        ):
    
    
    plot_type = plot_type.upper()
    
    if plot_type not in PLOT_TYPES:
        raise TypeError(f"{plot_type} is not a valid chart option. Valid plot options include 'BOX', 'BOXEN' or 'VIOLIN'")   
    
    label = ELEMENTS[element]['label']
    unit = ELEMENTS[element]['unit']
    
    xlabel = label
    
    if unit:
        xlabel += f' ({unit})'
        
    args = dict(x = element, 
                position = position,
                xlabel = f'{xlabel}',
               ) 
    
    if filters:
        args['y'] = "filter"
        args['ylabel'] = "Filter"
        filters_str = ", ".join(filters) if len(filters) > 1 else filters[0]
        
        if title:
            args['title']= title
        else:
            args['title'] =f"{label} distributions across filters ({filters_str})\n"
    else:
        
        if title:
            args['title']= title 
        else:
            args['title'] = f"{label} distributions across all filters"    
    
    
    cols = df["filter"].unique()

    if plot_type == "BOX":
        if filters:
            
            data = []
            
            for col in cols:
                data.append(df[df["filter"] == col][element])
            
            plot_template = BoxPlot(data = df, library = library, **args)
            if library == "seaborn":
                
                #Seaborn color customisation required
                for i, patch in enumerate(plot_template.ax.artists):
                    #print(patch)
                    patch.set_facecolor(COLOR_SCHEME[cols[i]])
            
            if library == "matplotlib":
                for i, patch in enumerate(plot_template.plot['boxes']):
                    patch.set(facecolor = COLOR_SCHEME[cols[i]])

                for median in plot_template.plot['medians']:
                    median.set_color('black')

                plot_template.ax.set_yticks(np.arange(1, len(cols) + 1), cols)

        else:
            
            plot_template = BoxPlot(**args, data = df, library = library, cache_data = cache_data)
            
            
            for median in plot_template.plot['medians']:
                median.set_color('black')
                
            for patch in plot_template.plot['boxes']:
                if element == "e":
                    patch.set(facecolor="#3CAE3F")
                if element == "q":
                    patch.set(facecolor="#FFE266")
                if element == "incl":
                    patch.set(facecolor="#ED4C4C")
                if element == "a":
                    patch.set(facecolor="#1C81A4")
        return plot_template
    
    elif plot_type == "VIOLIN":
        if filters:
            if library == "seaborn":
                #print(args)
                # decision on whether to have it only seaborn...
                # fix colors, titles etc.
                return ViolinPlot(data = df, library = library , cache_data = cache_data, **args)
            
            else:
                data = []
                for col in cols:
                    data.append(df[df["filter"] == col][element])

                plot_template = ViolinPlot(**args, data = data, cache_data = cache_data) # not supported

                plot_template.ax.set_yticks(np.arange(1, len(cols) + 1), cols)

                for i, pc in enumerate(plot_template.plot['bodies']):
                    pc.set_facecolor(COLOR_SCHEME[cols[i]])
                    pc.set_edgecolor('black')
        
        
        else:
            plot_template = ViolinPlot(**args, data = df)
            for pc in plot_template.plot['bodies']:
                pc.set_edgecolor("black") # add custom color here
            plot_template.ax.set_yticks([1], [''])

            
        for partname in ('cbars','cmins','cmaxes'):
            vp = plot_template.plot[partname]
            vp.set_edgecolor("black")
            vp.set_linewidth(1)
        
        return plot_template
    
    else:
        return BoxenPlot(**args, data= df, cache_data = cache_data)
        
        
    
def eccentricity(
    df : Optional[pd.DataFrame] = None,
    filters: Optional[list] = None,
    start_time : Optional[float] = None,
    end_time : Optional[float] = None,
    plot_type: Literal[PLOT_TYPES] = 'BOX',
    title : Optional[str] = None,
    cache_data: Optional[bool] = False,
    position : Optional[list] = None,
    **orbital_elements
):
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        conditions = []
       
        if start_time:
            conditions.append(diasource.c['midpointtai'] >= start_time)

        if end_time:
            conditions.append(diasource.c['midpointtai'] <= end_time)

        if filters:
            filters = validate_filters(list(set(filters)))
            conditions.append(diasource.c['filter'].in_(filters))
        
        conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
        
       
        
        stmt = select(
            distinct(mpcorb.c['ssobjectid']).label("ssobjectid") if distinct else mpcorb.c['ssobjectid'], mpcorb.c['e'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
        
        
        df = db.query(
            stmt.where(
                *conditions
            ) 
       )
        if df.empty:
            return empty_response(
                filters = filters,
                start_time = start_time,
                end_time = end_time,
                **orbital_elements
            )
    
    return base(
        df = df,
        filters = filters,
        start_time = start_time,
        end_time = end_time,
        plot_type = plot_type,
        title = title,
        element = 'e',
        position = position,
        cache_data = cache_data,
        **orbital_elements
    )
        
    
def perihelion(
    df : Optional[pd.DataFrame] = None,
    filters: Optional[list] = None,
    start_time : Optional[float] = None, end_time : Optional[float] = None,
    plot_type: Literal[PLOT_TYPES] = 'BOX',
    title : Optional[str] = None,
    cache_data: Optional[bool] = False,
    position : Optional[list] = None,
    **orbital_elements
):
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        conditions = []
       
        if start_time:
            conditions.append(diasource.c['midpointtai'] >= start_time)

        if end_time:
            conditions.append(diasource.c['midpointtai'] <= end_time)

        if filters:
            filters = validate_filters(list(set(filters)))
            conditions.append(diasource.c['filter'].in_(filters))

        conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
        
        
        stmt = select( distinct(mpcorb.c['ssobjectid']).label("ssobjectid") if distinct else mpcorb.c['ssobjectid'], mpcorb.c['q'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
        df = db.query(
            stmt.where(
                *conditions
            ) 
       )
        if df.empty:
            return empty_response(
                filters = filters,
                start_time = start_time,
                end_time = end_time,
                **orbital_elements
            )
        
    return base(
        df = df,
        filters = filters,
        start_time = start_time, end_time = end_time,
        **orbital_elements,
        plot_type = plot_type,
        title = title,
        element = 'q',
        position = position,
        cache_data = cache_data
    )
        
    
def inclination(
    df : Optional[pd.DataFrame] = None,
    filters: Optional[list] = None,
    start_time : Optional[float] = None, end_time : Optional[float] = None,
    plot_type: Literal[PLOT_TYPES] = 'BOX',
    title : Optional[str] = None,
    cache_data: Optional[bool] = False,
    distinct: Optional[bool] = False,
    position : Optional[list] = None,
    **orbital_elements
):
    
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        conditions = []
       
        if start_time:
            conditions.append(diasource.c['midpointtai'] >= start_time)

        if end_time:
            conditions.append(diasource.c['midpointtai'] <= end_time)

        if filters:
            filters = validate_filters(list(set(filters)))
            conditions.append(diasource.c['filter'].in_(filters))

        conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
                
        stmt =  select(mpcorb.c['incl'], diasource.c['filter'], distinct(mpcorb.c['ssobjectid']).label("ssobjectid") if distinct else mpcorb.c['ssobjectid']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
        
        df = db.query(
            stmt.where(
                *conditions
            ) 
       )
        if df.empty:
            return empty_response(
                filters = filters,
                start_time = start_time,
                end_time = end_time,
                **orbital_elements
            )
        
    return base(
        df = df,
        filters = filters,
        start_time = start_time, end_time = end_time,
        **orbital_elements,
        plot_type = plot_type,
        title = title,
        element = 'incl',
        position = position,
        cache_data = cache_data
    )
        
def semi_major_axis(
    df : Optional[pd.DataFrame] = None,
    filters: Optional[list] = None,
    start_time : Optional[float] = None,
    end_time : Optional[float] = None,
    plot_type: Literal[PLOT_TYPES] = 'BOX',
    title : Optional[str] = None,
    cache_data: Optional[bool] = False,
    distinct: Optional[bool] = False,
    position : Optional[list] = None,
    **orbital_elements
):
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        conditions = []
       
        if start_time:
            conditions.append(diasource.c['midpointtai'] >= start_time)

        if end_time:
            conditions.append(diasource.c['midpointtai'] <= end_time)

        if filters:
            filters = validate_filters(list(set(filters)))
            conditions.append(diasource.c['filter'].in_(filters))

        conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
        
        cols = []
        
        if distinct:
            cols.append(distinct(mpcorb.c['ssobjectid']).label('ssobjectid'))
                        
        else:
            cols.append(mpcorb.c['ssobjectid'])
                        
                
        stmt = select(distinct(mpcorb.c['ssobjectid']).label('ssobjectid') if distinct else mpcorb.c['ssobjectid'],mpcorb.c['q'], (mpcorb.c['q'] / (1 - mpcorb.c['e'])).label('a') , diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
        
        df = db.query(
            stmt.where(
                *conditions
            ) 
       )
        if df.empty:
            return empty_response(
                filters = filters,
                start_time = start_time,
                end_time = end_time,
                **orbital_elements
            )
        
    return base(
        df = df,
        filters = filters,
        start_time = start_time, end_time = end_time,
        **orbital_elements,
        plot_type = plot_type,
        title = title,
        element = 'a',
        position = position,
        cache_data = cache_data
    )
    