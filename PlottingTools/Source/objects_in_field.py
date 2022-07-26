'''
Plots of objects either heliocentric or topocentric views

'''


from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times, validate_filters, validate_orbital_elements
from database.format_time import format_times
from database.conditions import create_orbit_conditions



from plots import Plot, ScatterPlot
from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS
from sqlalchemy import select, func, text

from typing import Optional, Literal

import pandas as pd

def objects_in_field(
    df,
    filters: Optional[list] = None,
    start_time : Optional[float] = None, end_time : Optional[float] = None,
    title : Optional[str] = None,
    mpcdesignation: Optional[str] = None,
    ssobjectid: Optional[int] = None,
    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
    projection: Optional[Literal['2d', '3d']] = '2d',
    library : Optional[str] = "seaborn",
    cache_data: Optional[bool] = False,
    **orbital_elements
):
    
    if projection:
        projection = projection.lower()
    
    if filters:
        lc = ScatterPlot(data = pd.DataFrame(columns = df.columns.values) , x ="heliocentricx", y = "heliocentricy", z="heliocentricz" , projection = projection, library = library)
    
        if projection == "3d":
                lc.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black") ## add sun and earth?
        else:
                lc.ax.scatter(x = [0], y = [0], c = "black") ## add sun and earth?
        
        for _filter in filters:
            df_filter = df[df['filter'] == _filter]
            
            if not df_filter.empty:
                
                if projection == "2d":
                    lc.ax.scatter(x = df_filter['heliocentricx'] , y = df_filter['heliocentricy'], c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])
                    
                elif projection == '3d':
                    lc.ax.scatter(xs = df_filter['heliocentricx'] , ys = df_filter['heliocentricy'], zs=df_filter['heliocentricz'] ,c = COLOR_SCHEME[_filter], label=f"{_filter}", marker = FILTER_SYMBOLS[_filter])
                    
                   
        lc.ax.set_xlabel("X (au)")
        lc.ax.set_ylabel("Y (au)")
        if projection == "3d":
            lc.ax.set_zlabel("Z (au)")
        lc.ax.set_title(title if title else f"{mpcdesignation if mpcdesignation else ssobjectid if ssobjectid else ''} Orbit plot")            
        lc.ax.legend(loc="upper right")
                    
    else:
        if projection == '2d':
            lc = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", library = library)
            lc.ax.scatter(x = [0], y = [0], c = "black")
            lc.ax.set_xlabel("X (au)")
            lc.ax.set_ylabel("Y (au)")    
            lc.ax.set_title(title if title else f"{mpcdesignation if mpcdesignation else ssobjectid if ssobjectid else ''} Orbit plot")

        elif projection == '3d':
            lc = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", z = "heliocentricz", projection = '3d', library = library)
            lc.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black")
            lc.ax.set_xlabel("X (au)")
            lc.ax.set_ylabel("Y (au)")
            lc.ax.set_zlabel("Z (au)")
            lc.ax.set_title(title if title else f"{mpcdesignation if mpcdesignation else ssobjectid if ssobjectid else ''} Orbit plot")
    
    return lc
    
    
    