import os
import sys
import pathlib

PACKAGE_PARENT = pathlib.Path.cwd().parent
SCRIPT_DIR = PACKAGE_PARENT / 'Source'
sys.path.append(str(SCRIPT_DIR))

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from DataAccessLayer import create_connection_and_queryDB
from matplotlib import pyplot as plt
from plots.scatter import ScatterPlot
from plots.histogram import HistogramPlot
from plots.symbols import DEGREE, LAMBDA, BETA

from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times
from database.format_time import format_times
from database.conditions import create_orbit_conditions

from sqlalchemy import select, func


import math

from typing import Optional, Literal



def _detection_distributions(
    df,
    start_time : float, end_time : float,
    title : Optional[str] = None,
    #todo - timeframe : Literal["day", "monthly", "year"] = "day",
    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
    cache_data: Optional[bool] = False,
    **orbital_elements
):
    
    
    
    #conditions = create_orbit_conditions(**orbital_elements)
    
    '''
    df = db.query(
                select(diasource.c['midpointtai'], ).distinct(diasource.c['ssobjectid']).where(
                    diasource.c['midpointtai'] >= start_time,
                    diasource.c['midpointtai'] <= end_time
                )
            )
     
    '''  
    
    bins = [start_time + i for i in range(0, math.floor(end_time - start_time) + 1, 1)]
    
        
    df = df.sort_values(by = ['midpointtai'], ascending=True)

    df['datetime'] = [date[0:10] for date in format_times(df['midpointtai'].tolist(), _format="ISO")]
    
    hp = HistogramPlot(data = df, x="datetime", xbins = bins)
        
    hp.ax.set(yscale="log")
    hp.fig.suptitle(title if title else f"Detection distributions")
    
    hp.fig.autofmt_xdate()
    
    
    '''
    hp.ax.set_xlabel("Date")
    hp.ax.set_ylabel("No. of Detections")
    
    if time_format == "ISO":
        hp.ax.set_xticks(ticks = bins, labels = [date[0:10] for date in format_times(bins, _format="ISO")])
        
    '''  
    
    return hp


def object_detections(start: float, end: float):
    
    query = """
    SELECT
        ra, decl
    FROM
        diaSources
    WHERE
        midPointTai BETWEEN %(start)s AND %(end)s
    """
    

    df = create_connection_and_queryDB(query, dict(start=start, end=end)) # MJD


    return ScatterPlot(data = df, x = "ra", y = "decl", xlabel=f"R.A. ({DEGREE})", ylabel=f"Dec ({DEGREE})", title=f"Observations during the period {start}-{end}")

def ccd_visit(ccd_visit_id : int):
    query = """
    SELECT
        eclipticLambda as lon, eclipticBeta as lat, ccdVisitId, midPointTAI
    FROM
        diaSources
        JOIN ssSources USING(diaSourceId)
    WHERE
        ccdVisitId = %(ccd_visit_id)s
    """
    
    df = create_connection_and_queryDB(query, dict(ccd_visit_id = ccd_visit_id))
    
    return ScatterPlot(data = df, x = "lat", y = "lon", xlabel=f"Eccliptic {BETA} ({DEGREE})", ylabel=f"Eccliptic {LAMBDA} ({DEGREE})", title=f"CCD visit id {ccd_visit_id}")
    




