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
from plots.symbols import DEGREE, LAMBDA

from database import db
from database.schemas import diasource, mpcorb, ssobjects, sssource
from database.validators import validate_times
from database.format_time import format_times
from database.conditions import create_orbit_conditions

from sqlalchemy import select, func, distinct


import math

from typing import Optional, Literal

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


    return ScatterPlot(data = df, x = "ra", y = "decl", xlabel=f"R.A. ({degree})", ylabel=f"Dec ({DEGREE})", title=f"Observations during the period {start}-{end}")

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
    
    return ScatterPlot(data = df, x = "lat", y = "lon", xlabel=f"Eccliptic {beta} ({degree})", ylabel=f"Eccliptic {LAMBDA} ({DEGREE})", title=f"CCD visit id {ccd_visit_id}")

def _detection_distributions(
    start_time : float, end_time : float,
    #timeframe : Literal["day", "year"] = "day",
    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
    **orbital_elements
):
    
    start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
    
    conditions = create_orbit_conditions(**orbital_elements)
    

    data = db.query(
                select(diasource.c['midpointtai'], ).distinct(diasource.c['ssobjectid']).where(
                    diasource.c['midpointtai'] >= start_time,
                    diasource.c['midpointtai'] <= end_time
                )
            )
     
                
    bins = [start_time + i for i in range(0, math.floor(end_time - start_time), 1)]
    
    
    hp = HistogramPlot(data = data, x="midpointtai", xbins = bins)
        
    hp.ax.set(yscale="log")
    
    if time_format == "ISO":
        hp.ax.set_xticks(ticks = bins, labels = [date[0:10] for date in format_times(bins, _format="ISO")])
        
        hp.fig.autofmt_xdate()
        
    return hp
    
    




