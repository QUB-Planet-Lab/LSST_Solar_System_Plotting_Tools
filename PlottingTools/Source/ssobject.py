from database import db
from phase_curve import _phase_curve
from light_curve import _light_curve
from objects_in_field import objects_in_field

from typing import Optional, Literal

from sqlalchemy import select
from database.schemas import mpcorb, sssource, diasource, ssobjects
from math import cos, sqrt
from typing import Optional

import requests
import pandas as pd

from database.validators import validate_times, validate_filters
FILTERS = ["g", "r", "i", "z", "y", "u"]
class Object():
    #lazy_loading
    
    
    def __init__(self, ssobjectid: Optional[str] = None, mpcdesignation: Optional[str] = None, lazy_loading : Optional[bool] = True): 
        
        self.lazy_loading = lazy_loading
        
        self.mpcdesignation = mpcdesignation
        
        self.ssobjectid = str(ssobjectid) if ssobjectid else None
          
        self.T_J = None
        
        # Not sure if I can have two statements executed at once or open two connections with separate queries here.
        
        self.cols = [
            sssource.c['heliocentricx'],
            sssource.c['heliocentricy'],
            sssource.c['heliocentricz'],
            sssource.c['phaseangle'],
            sssource.c['topocentricdist'],
            sssource.c['heliocentricdist'],
            
            mpcorb.c['mpcdesignation'],
            
            diasource.c['ssobjectid'],
            diasource.c['filter'],
            diasource.c['magsigma'],
            diasource.c['mag'],
            diasource.c['midpointtai'], 
           ]
        
        for _filter in FILTERS:
                calc_mags = [ssobjects.c[f'{_filter}h'], ssobjects.c[f'{_filter}g12'], ssobjects.c[f'{_filter}herr'], ssobjects.c[f'{_filter}g12err'], ssobjects.c[f'{_filter}chi2']]
                
                for item in calc_mags:              
                    self.cols.append(item)
       
    
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
            self.orbital_parameters["a"] = None # None acceptable for now, may need refined
            
        try:
            self.orbital_parameters["Q"] = self.orbital_parameters["q"] * ((1 + self.orbital_parameters["e"])/ (1 - self.orbital_parameters["e"]))
        
        except:
            self.orbital_parameters["Q"] = None
    
    
        if lazy_loading == False:
            #load all data now
            #self.curve
            #self.orbit_data 
            
            self.curve_df = db.query( # self.get_curve_data()
                select(*self.cols).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(mpcorb.c["mpcdesignation"] == self.mpcdesignation)
            )
            
            #return empty dataframe if none
            if self.curve_df.empty:
                #add_empty response
                pass # empty response
            
            # Need to narrow down queries
            
            self.orbit_df = db.query( 
                select(diasource.c['filter'],
                    diasource.c['midpointtai'], 
                    sssource.c['heliocentricx'],
                    sssource.c['heliocentricy'],
                    sssource.c['heliocentricz']).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(mpcorb.c["mpcdesignation"] == self.mpcdesignation)
            )
            if self.orbit_df.empty:
                #add_empty response
                pass
                #return # empty response
        
        else:
            #better names required??
            self.curve_df = None
            self.orbit_df = None 
        
            
            
    def get_curve_data(self): # rename
        
        self.curve_df = db.query(
                select(*self.cols).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(mpcorb.c["mpcdesignation"] == self.mpcdesignation)
            )
        
        if self.curve_df.empty:
            #add empty response
            return 
        
        return self.curve_df
    
    
    def get_orbit_data(self):
        self.orbit_df = db.query( 
                select(diasource.c['filter'],
                    diasource.c['midpointtai'], 
                    sssource.c['heliocentricx'],
                    sssource.c['heliocentricy'],
                    sssource.c['heliocentricz']).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(mpcorb.c["mpcdesignation"] == self.mpcdesignation))
            
        if self.orbit_df.empty:
                #add_empty response
                pass
            
        return self.orbit_df
            
    
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

    def phase_curve(self, 
                    start_time: Optional[float] = None, 
                    end_time : Optional[float] = None,
                    filters: Optional[list] = None,
                    title : Optional[str] = None,
                    library : Optional[str] = "matplotlib",
                    fit = None,                    
                   ):
        
        if self.lazy_loading == True:
            #check if data exists first
            if self.curve_df is None:
                # get data
                df = self.get_curve_data()
                
            else: # clean-up names here
                df = self.curve_df.copy(deep = True) # not sure if this is optimal to make copies
        else:
            df = self.curve_df.copy(deep = True)

        # work on replot
        
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
        if filters:
            filters = validate_filters(list(set(filters)))
        
        if start_time:
            df = df.loc[df['midpointtai'] >= start_time].copy() # copy() silences warnings ~ effect on performance needs evaluated
        if end_time:
            df = df.loc[df['midpointtai'] <= end_time].copy()
        
        return _phase_curve(
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            df = df,
            filters = filters,
            title = title,
            library = library,
            fit = fit
        )
        
    
    def light_curve(self, 
                    filters: Optional[list] = None,
                    start_time : Optional[float] = None, end_time : Optional[float] = None,
                    title : Optional[str] = None,
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                    library: Optional[str] = "matplotlib"
                   ):
        if self.lazy_loading == True:
            if self.curve_df is None:
                # get data
                df = self.get_curve_data()
                
            else: # clean-up names here
                #data already here...
                df = self.curve_df.copy(deep = True)
        else:
            df = self.curve_df.copy(deep = True)
                    
        # work on replot
        
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
        if filters:
            filters = validate_filters(list(set(filters)))
        
        if start_time:
            df = df.loc[df['midpointtai'] >= start_time].copy() # copy() silences warnings ~ effect on performance needs evaluated
        if end_time:
            df = df.loc[df['midpointtai'] <= end_time].copy()
        
        
        return _light_curve(
            df = df,
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format,
            library = library
        )
    
    def plot_orbit(self,
                filters: Optional[list] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                projection: Optional[Literal['2d', '3d']] = '2d',
                library: Optional[str] = "matplotlib",
                **orbital_elements # is orbital elements needed?
                ): 
                # nice to animate this aswell with theoretical data if available
        
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
        if filters:
            filters = validate_filters(list(set(filters)))
            
        if self.lazy_loading == True:
            if self.orbit_df is None:
                # get data
                df = self.get_orbit_data()
                
            else: # clean-up names here
                #data already here...
                df = self.orbit_df.copy(deep = True)
        else:
            df = self.orbit_df.copy(deep = True)
            
        if start_time:
            df = df.loc[df['midpointtai'] >= start_time].copy() # copy() silences warnings ~ effect on performance needs evaluated
        if end_time:
            df = df.loc[df['midpointtai'] <= end_time].copy()
        

        return objects_in_field(
            df = df,
            #mpcdesignation = self.mpcdesignation,
            #ssobjectid = self.ssobjectid,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format,
            projection = projection,
            library = library,
            **orbital_elements
        )
    
    def find_jpl_matches(self, limit : Optional[int] = 20):
        t_j = round(self.tisserand, 3)
        
        
        query = '{"t_jup":%s}'%(str(t_j))
        #other parameters?
        
       
        resp = requests.get(f'https://www.asterank.com/api/asterank?query={query}&limit={limit}').json()
        
        df = pd.DataFrame.from_records(resp)

        return df
    
    def clear(
        self,
        curve_df : Optional[bool] = True,
        orbit_df : Optional[bool] = True
    ):
        if curve_df:
            self.curve_df = None
        if orbit_df:
            self.orbit_df = None
        
        return
    
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
        
    