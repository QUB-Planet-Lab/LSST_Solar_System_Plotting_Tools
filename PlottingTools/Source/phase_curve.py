from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times, validate_filter
from database.format_time import format_times

from typing import Literal, Optional
from sqlalchemy import select

from plots import ScatterPlot
from plots.symbols import DEGREE

def phase_curve(_filter: Optional[Literal['g','r','i','z','y', 'u']] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                mpcdesignation: Optional[str] = None
):

    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)


    cols = [diasource.c['magsigma'], diasource.c['filter'], mpcorb.c['mpcdesignation'], diasource.c['midpointtai'],diasource.c['mag'], sssource.c['phaseangle']]
    
    conditions = []
    
    if _filter:
        
        _filter = validate_filter(_filter)
           
        conditions.append(diasource.c['filter'] == _filter)
        
    if mpcdesignation:
        conditions.append(mpcorb.c['mpcdesignation'] == mpcdesignation)
   
    
    if start_time:
        conditions.append(diasource.c['midpointtai'] >= start_time)
    
    if end_time:
        conditions.append(diasource.c['midpointtai'] <= end_time)
    
    stmt = select(*cols).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)
    
    df = db.query(
        stmt
    )
    
    pc = ScatterPlot(data = df, x = "phaseangle", y="mag", yerr=df["magsigma"], title=title if title else f"Phase curve for {mpcdesignation}\n {start_time} - {end_time}", xlabel=f"Phase Angle ({DEGREE})", ylabel="Magnitude")
    
    pc.ax.invert_yaxis()
    
    return pc

