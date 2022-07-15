from plots.box import BoxPlot, BoxenPlot
from plots.violin import ViolinPlot
from plots.scatter import ScatterPlot
from plots.histogram import HistogramPlot
from plots.symbols import DEGREE
from plots.styles.filter_color_scheme import COLOR_SCHEME

from database import db
from database.schemas import DIASource, diasource, mpcorb
from database.validators import validate_times, validate_filters,\
    validate_perihelion, validate_inclination, validate_semi_major_axis, validate_orbital_elements
from database.format_time import format_times

from database.conditions import create_orbit_conditions
from database.empty_response import empty_response

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from typing import Optional, Literal

from sqlalchemy import select, func


PLOT_TYPES = ['BOX', 'BOXEN', 'VIOLIN']

ELEMENTS = {'e' : {'label': 'Eccentricity','unit' : None},\
            'a' : {'label': 'Semi-Major axis', 'unit': 'au'},\
            'peri' : {'label': 'Perihelion', 'unit': 'au'}, \
            'incl' : {'label' : 'Inclination', 'unit' : DEGREE}
           }

    
def orbital_relationships(
    x : Literal["incl", "peri", "e", "a"],
    y : Literal["incl", "peri", "e", "a"],
    start_time : Optional[float] = None, end_time : Optional[float] = None,
    title : Optional[str] = None,
    plot_type : Literal["scatter", "2d_hist", "2d_hex"] = "scatter",
    **orbital_elements
):
    
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)    
    
    if plot_type not in ["scatter", "2d_hist", "2d_hex"]:
        raise Exception("Plot type must be scatter, 2d_hist, 2d_hex")
    conditions = []
    
    if start_time:
        conditions.append(diasource.c['midpointtai'] >= start_time)
    
    if end_time:
        conditions.append(diasource.c['midpointtai'] <= end_time)
    
    
    conditions = create_orbit_conditions(conditions = conditions, **orbital_elements)
    
    if x == "a":
        qx = (mpcorb.c['peri'] / (1 - mpcorb.c['e'])).label('a')
    else:
        qx = mpcorb.c[x]
        
    if y == "a":
        qy = (mpcorb.c['peri'] / (1 - mpcorb.c['e'])).label('a')
    else:
        qy = mpcorb.c[y]
        
        
        
    df = db.query(
        select(
            func.distinct(mpcorb.c['ssobjectid']), qx , qy, diasource.c['filter']).join(
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

    if plot_type == "scatter":
        return ScatterPlot(data = df, x=x, y=y, xlabel=x, ylabel=y, title = title)
    
    if plot_type == "2d_hex":
        hp = HistogramPlot(data = df, x = x, y = y, projection="2d_hex")
        
        return hp
    
    if plot_type == "2d_hist":
        hp = HistogramPlot(data = df, x = x, y = y, projection="2d")
       
        return hp
    
def base(
         stmt,
         element, # e, incl, a, peri
         filters: Optional[list] = None,
         start_time : Optional[float] = None, end_time : Optional[float] = None,
         plot_type: Literal[PLOT_TYPES] = 'BOX',
         title : Optional[str] = None,
         **orbital_elements
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
        
    
    create_orbit_conditions(conditions = conditions, **orbital_elements)
        
        
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

    
    start_time, end_time = format_times([start_time, end_time], _format="ISO")
    label = ELEMENTS[element]['label']
    unit = ELEMENTS[element]['unit']
    xlabel = label
    if unit:
        xlabel += f' ({unit})'
    args = dict(x = element, 
                xlabel = f'{xlabel}', 
               ) 
    
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
    
    
    cols = df["filter"].unique()

    if plot_type == "BOX":
        if filters:
            

            data = []
            
            for col in cols:
                data.append(df[df["filter"] == col][element])
            
            plot_template = BoxPlot(**args, data = data)
            
            for i, patch in enumerate(plot_template.plot['boxes']):
                patch.set(facecolor = COLOR_SCHEME[cols[i]])

            for median in plot_template.plot['medians']:
                median.set_color('black')
                
            plot_template.ax.set_yticks(np.arange(1, len(cols) + 1), cols)
        else:
            plot_template = BoxPlot(**args, data = df)
            
            for median in plot_template.plot['medians']:
                median.set_color('black')
                
            for patch in plot_template.plot['boxes']:
                patch.set(facecolor="#3CAE3F") # customise
             
        return plot_template
    
    elif plot_type == "VIOLIN":
        if filters:
            data = []
            for col in cols:
                data.append(df[df["filter"] == col][element])
            
            plot_template = ViolinPlot(**args, data = data)

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
        return BoxenPlot(**args, data= df)
        
        
    
def eccentricity(filters: Optional[list] = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX',
                 title : Optional[str] = None,
                 **orbital_elements
                ):
    
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        plot_type = plot_type,
        title = title,
        element = 'e',
        **orbital_elements,
        stmt = select(
            func.distinct(mpcorb.c['ssobjectid']), mpcorb.c['e'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
        
    )
        
    
def perihelion(filters: Optional[list] = None,
               start_time : Optional[float] = None, end_time : Optional[float] = None,
               plot_type: Literal[PLOT_TYPES] = 'BOX',
               title : Optional[str] = None,
               **orbital_elements,
                  ):
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        **orbital_elements,
        plot_type = plot_type,
        title = title,
        element = 'peri',
        stmt = select(func.distinct(mpcorb.c['ssobjectid']), mpcorb.c['peri'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )
        
    
def inclination(filters: Optional[list] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                plot_type: Literal[PLOT_TYPES] = 'BOX',
                title : Optional[str] = None,
                **orbital_elements
               ):
    
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        **orbital_elements,
        plot_type = plot_type,
        title = title,
        element = 'incl',
        stmt = select(func.distinct(mpcorb.c['ssobjectid']),mpcorb.c['incl'], diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )

    
        
def semi_major_axis(filters: Optional[list] = None,
                 start_time : Optional[float] = None, end_time : Optional[float] = None,
                 plot_type: Literal[PLOT_TYPES] = 'BOX',
                 title : Optional[str] = None,
                 **orbital_elements
                ):
    
    return base(
        filters = filters,
        start_time = start_time, end_time = end_time,
        **orbital_elements,
        plot_type = plot_type,
        title = title,
        element = 'a',
        stmt = select(func.distinct(mpcorb.c['ssobjectid']).label('ssobjectid'), mpcorb.c['peri'], (mpcorb.c['peri'] / (1 - mpcorb.c['e'])).label('a') , diasource.c['filter']).join(
            diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    )

    