'''
Plots of objects either heliocentric or topocentric views

'''


from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times, validate_filters, validate_orbital_elements
from database.format_time import format_times

from plots import Plot, ScatterPlot
from plots.styles.filter_color_scheme import COLOR_SCHEME

from sqlalchemy import select, func, text

from typing import Optional, Literal

import pandas as pd

def objects_in_field(
    filters: Optional[list] = None,
    start_time : Optional[float] = None, end_time : Optional[float] = None,
    title : Optional[str] = None,
    mpcdesignation: Optional[str] = None,
    ssobjectid: Optional[int] = None,
    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
    projection: Optional[Literal['2d', '3d']] = '2d',
    **orbital_elements
):
    
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    cols = [
            diasource.c['filter'],
            diasource.c['midpointtai'], 
            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],
           ]
    
    conditions = []
    
    
    if filters:
        
        filters = validate_filters(list(set(filters)))
        conditions.append(diasource.c['filter'].in_(filters))
    
        
    if mpcdesignation:
        conditions.append(mpcorb.c['mpcdesignation'] == mpcdesignation)
   
    if ssobjectid:
        conditions.append(mpcorb.c['ssobjectid'] == ssobjectid)
    
    if start_time:
        conditions.append(diasource.c['midpointtai'] >= start_time)
    
    if end_time:
        conditions.append(diasource.c['midpointtai'] <= end_time)
    stmt = select(
            *cols
            ).\
        join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    
    if projection:
        projection = projection.lower()
    
        
    min_a, max_a, min_incl, max_incl, min_peri, max_peri, min_e, max_e = validate_orbital_elements(**orbital_elements)
    
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
        
    
    
    stmt = select(*cols).join(mpcorb, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

    # No need for third join currently
    
    df = db.query(
             stmt
    )
    
    if df.empty:
        if df.empty:
            query = f"""No results returned for your query:\n"""
        if filters:
            query += f"filters : {filters}\n"
        if start_time:
            query += f"start_time : {start_time}\n"
        if end_time:
            query += f"end_time : {end_time}\n"
        if mpcdesignation:
            query += f"mpcdesignation : {mpcdesignation}\n"
        if ssobjectid:
            query += f"ssobjectid : {ssobjectid}\n"
                
        query = query[0:-1]
        
        print(query)
        return # Is this the best way to return no results?
    
    if filters:
        lc = ScatterPlot(data = pd.DataFrame(columns = df.columns.values) , x ="heliocentricx", y = "heliocentricy", z="heliocentricz", projection = projection)
        for _filter in filters:
            df_filter = df[df['filter'] == _filter]
            
            if not df_filter.empty:
                if projection == '2d':
                    lc.ax.scatter(x = df_filter["heliocentricx"], y = df_filter["heliocentricy"], label=_filter,  c = COLOR_SCHEME[_filter])
        # add filter to plot
                elif projection == '3d':
                    
                    lc.ax.scatter(xs = df_filter["heliocentricx"], ys = df_filter["heliocentricy"], zs = df_filter["heliocentricz"], label=_filter, c = COLOR_SCHEME[_filter])
                   
        lc.ax.set_xlabel("X (au)")
        lc.ax.set_ylabel("Y (au)")
        lc.ax.set_zlabel("Z (au)")
        lc.ax.set_title(title if title else f"{mpcdesignation if mpcdesignation else ssobjectid if ssobjectid else ''} Orbit plot")            
        lc.ax.legend(loc="upper right")
                    
    else:
        if projection == '2d':
            lc = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy")
            lc.ax.scatter(x = [0], y = [0], c = "black")
            lc.ax.set_xlabel("X (au)")
            lc.ax.set_ylabel("Y (au)")    
            lc.ax.set_title(title if title else f"{mpcdesignation if mpcdesignation else ssobjectid if ssobjectid else ''} Orbit plot")
            
            

        elif projection == '3d':
            lc = ScatterPlot(data = df, x = "heliocentricx", y = "heliocentricy", z = "heliocentricz", projection = '3d')
            lc.ax.scatter(xs = [0], ys = [0], zs=[0] ,c = "black")
            lc.ax.set_xlabel("X (au)")
            lc.ax.set_ylabel("Y (au)")
            lc.ax.set_zlabel("Z (au)")
            lc.ax.set_title(title if title else f"{mpcdesignation if mpcdesignation else ssobjectid if ssobjectid else ''} Orbit plot")

    return lc
    
    
    