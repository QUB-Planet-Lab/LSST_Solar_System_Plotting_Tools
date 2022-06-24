import os
import sys
import pathlib

PACKAGE_PARENT = pathlib.Path.cwd().parent
SCRIPT_DIR = PACKAGE_PARENT / 'Source'
sys.path.append(str(SCRIPT_DIR))

import numpy as np
from DataAccessLayer import create_connection_and_queryDB
from matplotlib import pyplot as plt
from plots.scatter import ScatterPlot
from plots.symbols import degree, beta, _lambda


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


    return ScatterPlot(data = df, x = "ra", y = "decl", xlabel=f"R.A. ({degree})", ylabel=f"Dec ({degree})", title=f"Observations during the period {start}-{end}")

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
    
    return ScatterPlot(data = df, x = "lat", y = "lon", xlabel=f"Eccliptic {beta} ({degree})", ylabel=f"Eccliptic {_lambda} ({degree})", title=f"CCD visit id {ccd_visit_id}")
    
    
    
    




