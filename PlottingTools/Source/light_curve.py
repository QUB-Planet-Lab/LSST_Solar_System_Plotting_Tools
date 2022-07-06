from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times, validate_filter
from database.format_time import format_times

from plots import Plot, ScatterPlot

from sqlalchemy import select

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from typing import Optional, Literal
import pandas as pd

def light_curve(_filter: Optional[Literal['g','r','i','z','y']] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                mpcdesignation: Optional[str] = None,
                ssobjectid: Optional[int] = None,
                time_format: Optional[Literal['ISO', 'MJD']] = 'ISO'
               ):
        
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    
    if not ssobjectid and not mpcdesignation:
        # More needed to handle both when ssobjectid and mpcdesingation is specified?
        raise Exception("You must provide either an mpcdesignation or an ssobjectid to this function")
        
    
    cols = [
            diasource.c['magsigma'],
            diasource.c['filter'],
            mpcorb.c['mpcdesignation'],
            diasource.c['midpointtai'],
            diasource.c['mag'],
            diasource.c['ssobjectid'],
           ]
    
    conditions = []
    
    if _filter:
        
        _filter = validate_filter(_filter)
        '''
        for col in [ssobjects.c[f'{_filter}h'],
            ssobjects.c[f'{_filter}herr']]:
        
            cols.append(
                col
            )
        '''
        conditions.append(diasource.c['filter'] == _filter)
    
        
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
    
    #if _filter:
    #    stmt.join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid'])
    
    stmt = select(*cols).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).where(*conditions)
    # No need for third join currently
    
    df = db.query(
             stmt
    )
    
    if df.empty:
        if df.empty:
            query = f"""No results returned for your query:\n"""
        if _filter:
            query += f"filter : {_filter}\n"
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
    
    if time_format == 'ISO':
        df['datetimes'] = pd.to_datetime(format_times(df['midpointtai'].to_list(), _format = "ISO"))
        x = "datetimes"
        xlabel = "Date"
    elif time_format == 'MJD':
        x = "midpointtai"
        xlabel = "Time (MJD)"
    

    lc = ScatterPlot(data = df, x = x, y = "mag", yerr=df["magsigma"], title=title if title else f"{mpcdesignation if mpcdesignation else ssobjectid}\n {start_time} - {end_time}" + f"\n {_filter} filter", xlabel = xlabel, ylabel="Magnitude")

    
    lc.fig.autofmt_xdate()
    lc.ax.invert_yaxis()

    return lc
    
    