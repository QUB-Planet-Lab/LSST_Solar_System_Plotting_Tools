from database import db
from phase_curve import _phase_curve
from light_curve import _light_curve
from objects_in_field import objects_in_field

from typing import Optional, Literal

from sqlalchemy import select
from database.schemas import mpcorb
from math import cos, sqrt
from typing import Optional

import requests
import pandas as pd

class Object():
    def __init__(self, ssobjectid: Optional[str] = None, mpcdesignation: Optional[str] = None): # diasourceid?
        #https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=1999%20AN10
        
        #https://cneos.jpl.nasa.gov/about/neo_groups.html
        
        
        self.mpcdesignation = mpcdesignation
        
        self.ssobjectid = str(ssobjectid) if ssobjectid else None
        
        
        self.T_J = None
        
        stmt = select(mpcorb.c["e"], mpcorb.c["q"], mpcorb.c["peri"],# 
                   mpcorb.c["incl"], mpcorb.c["node"],
                   mpcorb.c["n"], mpcorb.c["epoch"], mpcorb.c['ssobjectid'], mpcorb.c['mpcdesignation'],  mpcorb.c['mpcnumber'], mpcorb.c['fulldesignation']  #mpcorb.c["m"]
                  )
        
        if mpcdesignation:
            stmt = stmt.where(mpcorb.c["mpcdesignation"] == mpcdesignation)
        
        elif ssobjectid:
            stmt = stmt.where(mpcorb.c["ssobjectid"] == ssobjectid)
        
        else:
            raise Exception("An mpcdesignation or a ssobjectid must be provided")
        
        self.orbital_parameters = db.query(
            stmt
        )
        
        if self.orbital_parameters.empty:
            #add empty_response here.
            raise Exception("No results returned")
        
        if not self.ssobjectid:
            
            self.ssobjectid = str(self.orbital_parameters['ssobjectid'][0])
        
        if not self.ssobjectid:

            self.mpcdesignation = self.orbital_parameters['mpcdesignation'][0].strip()
            
        
        self.orbital_parameters = self.orbital_parameters.drop(['mpcdesignation', 'ssobjectid', 'mpcnumber', 'fulldesignation'], axis=1)
        
        
        try:
            self.orbital_parameters["a"] = self.orbital_parameters["q"] / (1 - self.orbital_parameters["e"])
        except:
            self.orbital_parameters["a"] = None
            
        try:
            self.orbital_parameters["Q"] = self.orbital_parameters["q"] * ((1 + self.orbital_parameters["e"])/ (1 - self.orbital_parameters["e"]))
        
        except:
            self.orbital_parameters["Q"] = None
        
    @property
    def tisserand(self):
        if not self.T_J:
            a_J = 5.2038 # au
            if self.orbital_parameters['e'][0] < 1:

                self.T_J = a_J / self.orbital_parameters['a'][0] + 2 * cos(self.orbital_parameters['incl'][0]) * sqrt(self.orbital_parameters['a'][0] / a_J * (1 - self.orbital_parameters['e'][0]**2))

                return self.T_J
            else:
                print("Tisserand parameter is undefined for this object")
                return
        else:
            return self.T_J
    
    
    def find_jpl_matches(self, limit : Optional[int] = 20):
        t_j = round(self.tisserand, 3)
        
        
        query = '{"t_jup":%s}'%(str(t_j))
        #other parameters?
        
       
        resp = requests.get(f'https://www.asterank.com/api/asterank?query={query}&limit={limit}').json()
        
        df = pd.DataFrame.from_records(resp)

        return df
    '''
    # TODO
    @property
    def classification(self):
        #get from JPL
        #https://ssd-api.jpl.nasa.gov/doc/sb_ident.html
        # write call to JPL API
        
        query = '{"ref":"%s"}'%(str(self.mpcdesignation))
        print(f"http://asterank.com/api/mpc?query={query}&limit=1")
        resp = requests.get(f"http://asterank.com/api/mpc?query={query}&limit=1").json()
        print(resp)
        prov_des = resp["prov_des"]

        resp = requests.get(f"https://ssd-api.jpl.nasa.gov/sbdb.api?alt-des=1&alt-orbits=1&ca-data=1&ca-time=both&ca-tunc=both&cd-epoch=1&cd-tp=1&discovery=1&full-prec=1&nv-fmt=both&orbit-defs=1&phys-par=1&r-notes=1&r-observer=1&radar-obs=1&sat=1&sstr={prov_des}&utf8=1&vi-data=1&www=1").json()

        if resp:
                           print(resp["orbit"]["orbit_class"])
        else:
                           print("Cannot find the object given by ...")
     '''       
                            
        
    
    def phase_curve(self, 
                    start_time: Optional[float] = None, 
                    end_time : Optional[float] = None,
                    filters: Optional[list] = None,
                    title : Optional[str] = None,
                   ):
        return _phase_curve(
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            start_time = start_time,
            end_time = end_time,
            filters = filters,
            title = title
        )
        
    
    def light_curve(self, 
                    filters: Optional[list] = None,
                    start_time : Optional[float] = None, end_time : Optional[float] = None,
                    title : Optional[str] = None,
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO'
                   ):
        return _light_curve(
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format
        )
    
    def plot_orbit(self,
                filters: Optional[list] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                projection: Optional[Literal['2d', '3d']] = '2d',
                **orbital_elements
                ): 
                # nice to animate this aswell with theoretical data if available
        return objects_in_field(
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format,
            projection = projection,
            **orbital_elements
        )
        
    