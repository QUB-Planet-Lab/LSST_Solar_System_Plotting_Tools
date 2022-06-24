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
from sbpy.photometry import HG
from typing import Literal
from plots.symbols import degree

def phase_curve(mpc_designation : str, _filter: Literal['g','r','i','z','y', 'u']):
    query = f"""
            SELECT
                mpcdesignation, ssObjects.ssObjectId, mag, magSigma, filter, midPointTai as mjd, ra, decl, phaseAngle,
                topocentricDist, heliocentricDist
            FROM
                mpcorb
                JOIN ssObjects USING (ssobjectid)
                JOIN diaSources USING (ssobjectid)
                JOIN ssSources USING (diaSourceid)
            WHERE
                mpcdesignation = '{mpc_designation}' and filter='{_filter}'
        """
    
    df = create_connection_and_queryDB(query, dict(mpcdesignation=mpc_designation, _filter = _filter))
          
    df["cmag"] = df["mag"] - 5*np.log10(df["topocentricdist"]*df["heliocentricdist"])
    
    
    plt.errorbar(df["phaseangle"], df["cmag"], df["magsigma"], ls='none')
    plt.gca().invert_yaxis()
    plt.xlabel(f"Phase Angle ({degree})")
    plt.ylabel(f"Distance corrected {_filter} magnitude")
    plt.title(f'Phase curve for {df["mpcdesignation"].iloc[0].strip()}, {_filter} band')
    
    
    #Add phase curve
    ssoId = int(df["ssobjectid"].iloc[0])
    
    hg = create_connection_and_queryDB(f"SELECT {_filter}H, {_filter}G12, {_filter}HErr, {_filter}G12Err, {_filter}Chi2 FROM ssObjects WHERE ssObjectId=%(ssoId)s", dict(ssoId=ssoId))
    
    
    H, G, sigmaH, sigmaG, chi2dof = hg.iloc[0]
    _ph = sorted(df["phaseangle"])
    _mag = HG.evaluate(np.deg2rad(_ph), H, G)
    plt.plot(_ph, _mag)
    
    plt.savefig(f"{mpc_designation}_phase_curve.png")
    return 