from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times, validate_filters
from database.format_time import format_times
from database.empty_response import empty_response

from typing import Literal, Optional
from sqlalchemy import select

from plots import ScatterPlot
from plots.symbols import DEGREE
from plots.styles.filter_color_scheme import COLOR_SCHEME
from plots.styles.filter_symbols import FILTER_SYMBOLS

import pandas as pd
import numpy as np

from sbpy.photometry import HG, HG12, HG1G2

    
FIT = [None, 'HG'] #, 'HG12', 'HG1G2']

def _phase_curve(
                df : Optional[pd.DataFrame] = None , #dataframe
                filters: Optional[list] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                mpcdesignation: Optional[str] = None,
                ssobjectid: Optional[int] = None,
                library : Optional[str] = "matplotlib",
                fit = None, # FIT,
                cache_data: Optional[bool] = False
):
    if fit:
        fit = fit.upper()
    
    if fit not in FIT:
        raise Exception(f"{fit} is not a valid fit option. Valid options include {FIT}")
        
    if df is None:
        
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)

            
        cols = [diasource.c['magsigma'], diasource.c['filter'], mpcorb.c['mpcdesignation'], diasource.c['ssobjectid'], diasource.c['midpointtai'],diasource.c['mag'], sssource.c['phaseangle'], sssource.c['topocentricdist'], sssource.c['heliocentricdist']]
            
        conditions = []
    
        if filters:

            filters = validate_filters(list(set(filters)))
            conditions.append(diasource.c['filter'].in_(filters))


            for _filter in filters:
                calc_mags = [ssobjects.c[f'{_filter}h'], ssobjects.c[f'{_filter}g12'], ssobjects.c[f'{_filter}herr'], ssobjects.c[f'{_filter}g12err'], ssobjects.c[f'{_filter}chi2']]
                for item in calc_mags:              
                    cols.append(item)

        if mpcdesignation:
            conditions.append(mpcorb.c['mpcdesignation'] == mpcdesignation)
        if ssobjectid:
            conditions.append(mpcorb.c['ssobjectid'] == ssobjectid)

        elif not mpcdesignation and not ssobjectid:
            raise Exception("An mpcdesignation or ssobjectid must be provided")

        stmt = select(*cols).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

        df = db.query(
            stmt
        )

        
        if df.empty:
            empty_response()
            return
    
    df["cmag"] = df["mag"] - 5*np.log10(df["topocentricdist"]*df["heliocentricdist"])
    
    if filters:
        #note is yerr = 'magsigma'?
        pc = ScatterPlot(data = pd.DataFrame(columns = df.columns.values), x = "phaseangle", y="mag", title=title if title else f"Phase curve for {mpcdesignation if mpcdesignation else ssobjectid}\n", xlabel=f"Phase Angle ({DEGREE})", ylabel="Reduced magnitude", library = library, cache_data = cache_data)
        
                         
        for _filter in filters:
            df_filter = df[df['filter'] == _filter]
            if not df_filter.empty:
                pc.ax.errorbar(data = df_filter , x = "phaseangle", y = "cmag", yerr=df_filter['magsigma'], label=_filter, marker=FILTER_SYMBOLS[_filter], c = COLOR_SCHEME[_filter], ls = 'none')
                
                if fit == "HG":    
                    try:
                        _ph = sorted(df_filter["phaseangle"])
                        _mag = HG.evaluate(np.deg2rad(_ph), df_filter[f'{_filter}h'], df_filter[f'{_filter}g12err'])
                        pc.ax.plot(_ph, _mag, c = COLOR_SCHEME[_filter])
                    except:
                        print("Unable to append HG fit to phase curve.")
                '''
                #TO-DO - fit
                if fit == "HG1G2":
                    _ph = sorted(df_filter["phaseangle"])
                    _mag = HG1G2.evaluate(np.deg2rad(_ph), df_filter[f'{_filter}h'], df_filter[f'{_filter}g12'])
                    pc.ax.plot(_ph, _mag, c = COLOR_SCHEME[_filter]) 
                if fit == "HG12": 
                    _ph = sorted(df_filter["phaseangle"])
                    _mag = HG12.evaluate(np.deg2rad(_ph), df_filter[f'{_filter}h'], df_filter[f'{_filter}g12']) # g12
                    pc.ax.plot(_ph, _mag, c = COLOR_SCHEME[_filter])  
                '''  
                    
            pc.ax.legend(loc="upper right")        
            pc.data = df
    else:
        pc = ScatterPlot(data = df, x = "phaseangle", y="cmag", yerr=df["magsigma"], title=title if title else f"Phase curve for {mpcdesignation if mpcdesignation else ssobjectid}\n", xlabel=f"Phase Angle ({DEGREE})", ylabel="Reduced Magnitude", library = library, cache_data = cache_data)

    pc.ax.invert_yaxis()
    
    return pc
    
