import sys

sys.path.append("../Source")

from typing import Optional, Literal

from database import db
from database.validators import validate_times, validate_filters, validate_orbital_elements
from database.conditions import create_orbit_conditions
from database.format_time import format_times
from database.schemas import diasource, sssource
from database.empty_response import empty_response


from sqlalchemy import select

import pandas as pd

from plots import ScatterPlot, Histogram2D, HexagonalPlot

from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS
from plots.add_planets import add_planets

from .handle_query import handle_query

cols = [
            diasource.c['filter'],
            diasource.c['midpointtai'], 
            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],
            diasource.c['mag']
           ]

def plot_limits(ax, _max):
    if _max:
        ax.set_xlim(-(_max), _max)
        ax.set_ylim(-(_max), _max)

def planet_plot(ax, x, y):
    df_max_x = abs(x.max()) 
    df_min_x = abs(x.min())

    df_max_y = abs(y.max()) 
    df_min_y = abs(y.min())

    df_max = df_max_x if df_max_x >= df_max_y else df_max_y
    df_min = df_min_x if df_min_x >= df_min_y else df_min_y

    add_planets(ax = ax, xlim = df_max if df_max >= df_min else df_min)

def _heliocentric_view(
    start_time,
    end_time,
    conditions,
    filters: Optional[list] = None,
    title : Optional[str] = None,
    projection: Optional[Literal['2d', '3d']] = '2d',
    library: Optional[str] =  "seaborn",
    cache_data: Optional[bool] = False,
    planets: Optional[bool] = False,
    **orbital_elements
):    
        
    df = handle_query(cols, conditions)
    
    if df.empty:
        return empty_response(
            start_time = start_time,
            end_time = end_time,
            filters = filters,
            **orbital_elements
        )
    
    if projection:
        projection = projection.lower()

        if filters:
            sp = ScatterPlot(data = pd.DataFrame(columns = df.columns.values) , x ="heliocentricx", y = "heliocentricy", z="heliocentricz" , projection = projection, library = library, cache_data = cache_data, data_copy = df)

            if projection == "3d":
                    sp.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black") 
            else:
                    sp.ax.scatter(x = [0], y = [0], c = "black")

            for _filter in filters:
                df_filter = df[df['filter'] == _filter]

                if not df_filter.empty:

                    if projection == "2d":
                        sp.ax.scatter(x = df_filter['heliocentricx'] , y = df_filter['heliocentricy'], c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])

                    elif projection == '3d':
                        sp.ax.scatter(xs = df_filter['heliocentricx'] , ys = df_filter['heliocentricy'], zs=df_filter['heliocentricz'] ,c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])
                        sp.ax.legend(loc="upper right")
            sp.ax.legend()
        else:
            if projection == '2d':
                sp = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data)
                sp.ax.scatter(x = [0], y = [0], c = "black")

            elif projection == '3d':
                sp = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", z = "heliocentricz", projection = '3d', library = library, cache_data = cache_data)
                sp.ax.scatter(xs = [0], ys = [0], zs=[0] , c = "black")

    sp.ax.set_xlabel("Heliocentric X (au)")
    sp.ax.set_ylabel("Heliocentric Y (au)")


    if projection == "3d":
        sp.ax.set_zlabel("Heliocentric Z (au)")
    sp.ax.set_title(title if title else f"")  
    
    
    
    _max = None
        
    if 'max_hd' in  orbital_elements:
        _max = orbital_elements['max_hd']
    
    plot_limits(ax = sp.ax, _max = _max)
    
    sp.fig.set_figwidth(8)
    sp.fig.set_figheight(8)

    if planets and projection != "3d":
        planet_plot(ax = sp.ax, x = df['heliocentricx'], y = df['heliocentricy'])
         

    return sp


def _heliocentric_histogram(
    start_time,
    end_time,
    conditions,
    filters: Optional[list] = None,
    title : Optional[str] = None,
    marginals: Optional[bool] = True,
    library: Optional[str] =  "seaborn",
    cache_data: Optional[bool] = False,
    planets: Optional[bool] = False,
    **orbital_elements
):
    df = handle_query(cols, conditions)
    
    if df.empty:
        return empty_response(
            start_time = start_time,
            end_time = end_time,
            filters = filters,
            **orbital_elements
        )
    
    sp = Histogram2D(data = df, x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data, xlabel = "Heliocentric X (au)", ylabel = "Heliocentric Y (au)", marginals = marginals )

    _max = None

    if 'max_hd' in  orbital_elements:
        _max = orbital_elements['max_hd']
    
    plot_limits(ax = sp.ax[0] if marginals else sp.ax, _max = _max)

    if planets:
        planet_plot(ax = sp.ax[0], x = df['heliocentricx'], y = df['heliocentricy'])
    
    sp.fig.set_figwidth(8)
    sp.fig.set_figheight(8)


    return sp

def _heliocentric_hexplot(
    start_time,
    end_time,
    conditions,
    filters: Optional[list] = None,
    title : Optional[str] = None,
    marginals: Optional[bool] = True,
    library: Optional[str] =  "seaborn",
    cache_data: Optional[bool] = False,
    planets: Optional[bool] = False,
    **orbital_elements
):
    
    
    df = handle_query(cols, conditions)
    
    if df.empty:
        return empty_response(
            start_time = start_time,
            end_time = end_time,
            filters = filters,
            **orbital_elements
        )
    
    sp = HexagonalPlot(data = df, x = "heliocentricx", y = "heliocentricy", library = library, cache_data = cache_data, xlabel = "Heliocentric X (au)", ylabel = "Heliocentric Y (au)")

    _max = None

    if 'max_hd' in  orbital_elements:
        _max = orbital_elements['max_hd']

    plot_limits(ax = sp.ax[0] if marginals else sp.ax, _max = _max)


    if planets:
        planet_plot(ax = sp.ax[0], x = df['heliocentricx'], y = df['heliocentricy'])
    
    sp.fig.set_figwidth(8)
    sp.fig.set_figheight(8)

    return sp