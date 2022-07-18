from database import db
from phase_curve import _phase_curve
from light_curve import _light_curve
from objects_in_field import objects_in_field

from typing import Optional, Literal

from sqlalchemy import select
from database.schemas import mpcorb

class Object():
    def __init__(self, ssobjectid: Optional[str] = None, mpcdesignation: Optional[str] = None): # diasourceid?
        #https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=1999%20AN10
        
        #https://cneos.jpl.nasa.gov/about/neo_groups.html
        
        self.ssobjectid = ssobjectid
        self.mpcdesignation = mpcdesignation
        
        stmt = select(mpcorb.c["e"], mpcorb.c["q"], mpcorb.c["peri"],# (mpcorb.c['peri'] / (1 - mpcorb.c['e'])).label('a'),
                   mpcorb.c["incl"], mpcorb.c["node"],
                   mpcorb.c["n"], mpcorb.c["epoch"], #mpcorb.c["m"]
                   #(((1 + mpcorb.c['e'])/(1 - mpcorb.c['e'])) * mpcorb.c['q']).label("Q")
                  )
        
        if self.mpcdesignation:
            stmt = stmt.where(mpcorb.c["mpcdesignation"] == self.mpcdesignation)
        
        elif self.ssobjectid:
            stmt = stmt.where(mpcorb.c["ssobjectid"] == self.ssobjectid)
        
        else:
            raise Exception("An mpcdesignation or a ssobjectid must be provided")
        
        self.orbital_parameters = db.query(
            stmt
        )
        
        if self.orbital_parameters.empty:
            raise Exception("No results returned")
        try:
            # Need to add cometary and Keplarian classification here
            self.orbital_parameters["a"] = self.orbital_parameters["q"] / (1 - self.orbital_parameters["e"])
        except:
            self.orbital_parameters["a"] = None
            
        try:
            
            self.orbital_parameters["Q"] = self.orbital_parameters["q"] * ((1 + self.orbital_parameters["e"])/ (1 - self.orbital_parameters["e"]))
        
        except:
            self.orbital_parameters["Q"] = None
        
        
    @property
    def classification(self):
        #get from JPL
        #https://ssd-api.jpl.nasa.gov/doc/sb_ident.html
        # write call to JPL API
        pass
    
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
        
    