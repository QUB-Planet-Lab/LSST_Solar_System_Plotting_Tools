from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times, validate_filters
from database.format_time import format_times
from database.empty_response import empty_response


from plots import Plot, ScatterPlot

from sqlalchemy import select

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from typing import Optional, Literal
import pandas as pd

from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS

pd.options.mode.chained_assignment = None  # default='warn'

def _light_curve(
                df : Optional[pd.DataFrame] = None,   
                filters: Optional[list] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                mpcdesignation: Optional[str] = None,
                ssobjectid: Optional[int] = None,
                time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                library: Optional[str] = "matplotlib",
                cache_data: Optional[bool] = False
               ):
    
    
    if df is None:
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)

        if not ssobjectid and not mpcdesignation:
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


        stmt = select(*cols).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).where(*conditions)

        df = db.query(
             stmt
        )

        if df.empty: # add empty response here
            return empty_response()

        
        
    if time_format == 'ISO':
        df['datetimes'] = pd.to_datetime(format_times(df['midpointtai'].to_list(), _format = "ISO"))
        x = "datetimes"
        xlabel = "Date"
    elif time_format == 'MJD':
        x = "midpointtai"
        xlabel = "Time (MJD)"
    
    if filters:
        lc = ScatterPlot(data = pd.DataFrame(columns = df.columns.values) , x = x, y = "mag", title=title if title else f"{mpcdesignation if mpcdesignation else ssobjectid}\n", xlabel = xlabel, ylabel="Magnitude", library = library, cache_data = cache_data)

        for _filter in filters:
            df_filter = df[df['filter'] == _filter]
            if not df_filter.empty:
                lc.ax.errorbar(data = df_filter , x = x, y = "mag", yerr=df_filter['magsigma'], label=_filter, c = COLOR_SCHEME[_filter], marker=FILTER_SYMBOLS[_filter], ls='none')
        # add filter to plot
        lc.ax.legend(loc="upper right")        
        lc.data = df
    else:
        lc = ScatterPlot(data = df , x = x, y = "mag", title=title if title else f"{mpcdesignation if mpcdesignation else ssobjectid}\n", xlabel = xlabel, ylabel="Magnitude", library = library, cache_data = cache_data)
        
    lc.fig.autofmt_xdate()
    lc.ax.invert_yaxis()
    
    return lc
        

    
    