from database import db
from phase_curve import _phase_curve
from light_curve import _light_curve
from objects_in_field import _plot_orbit

from typing import Optional, Literal

from sqlalchemy import select
from database.schemas import mpcorb, sssource, diasource, ssobjects
from database.empty_response import empty_response

from math import cos, sqrt
from typing import Optional

import requests
import pandas as pd
import numpy as np

from database.validators import validate_times, validate_filters
FILTERS = ["g", "r", "i", "z", "y", "u"]

class Object():
        
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
        
        
        if self.T_J:
            self.orbital_parameters['tisserand'] = self.T_J
            
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
            self.curve_df = db.query( # self.get_curve_data()
                select(*self.cols).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(mpcorb.c["mpcdesignation"] == self.mpcdesignation)
            )
            
            if self.curve_df.empty:
                return empty_response()
                       
            self.orbit_df = db.query( 
                select(diasource.c['filter'],
                    diasource.c['midpointtai'], 
                    sssource.c['heliocentricx'],
                    sssource.c['heliocentricy'],
                    sssource.c['heliocentricz']).join(ssobjects, ssobjects.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(diasource, diasource.c['ssobjectid'] == mpcorb.c['ssobjectid']).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(mpcorb.c["mpcdesignation"] == self.mpcdesignation)
            )
            
            if self.orbit_df.empty:
                return empty_response()
        
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
                empty_response()
                return
                
        return self.orbit_df
            
    
    @property
    def tisserand(self):
        if not self.T_J:
            a_J = 5.2038 # au
            if self.orbital_parameters['e'][0] < 1:

                self.T_J = a_J / self.orbital_parameters['a'][0] + 2 * cos(self.orbital_parameters['incl'][0]) * sqrt(self.orbital_parameters['a'][0] / a_J * (1 - self.orbital_parameters['e'][0]**2))
                
                self.orbital_parameters['tisserand'] = self.T_J

                
                
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
                    cache_data: Optional[bool] = False,
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

        
        start_time, end_time = validate_times(start_time = start_time, end_time = end_time)
        
        filter_cols = []
        if filters:
            filters = validate_filters(list(set(filters)))
            for _filter in filters:
                filter_cols.extend([f'{_filter}h', f'{_filter}g12err', f'{_filter}g12'])
                
        if start_time:
            df = df.loc[df['midpointtai'] >= start_time].copy() 
        if end_time:
            df = df.loc[df['midpointtai'] <= end_time].copy()
        
        return _phase_curve(
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            df = df[['filter','mag', 'magsigma', 'topocentricdist', 'heliocentricdist', 'phaseangle', *filter_cols]],
            filters = filters,
            title = title,
            library = library,
            fit = fit,
            cache_data = cache_data
        )
    
    def single_phase_curves(
        self,
        filters: list = FILTERS,
        title: str = None,
        fit = None,
        cache_data: Optional[bool] = False
    ):
        
        filters = validate_filters(filters)
        
        plots = []

            
        for _filter in filters:
            pc = self.phase_curve(
                filters = [_filter],
                title = title,
                fit = fit,
                cache_data = cache_data
            )
            plots.append(pc)
            
        
        return plots
    
    def light_curve(self, 
                    filters: Optional[list] = None,
                    start_time : Optional[float] = None, end_time : Optional[float] = None,
                    title : Optional[str] = None,
                    time_format: Optional[Literal['ISO', 'MJD']] = 'ISO',
                    library: Optional[str] = "matplotlib",
                    cache_data: Optional[bool] = False
                   ):
        if self.lazy_loading == True:
            if self.curve_df is None:
                # get data
                df = self.get_curve_data()
                
            else: # clean-up names here
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
            df = df[['filter', 'mag', 'midpointtai', 'magsigma']],
            mpcdesignation = self.mpcdesignation,
            ssobjectid = self.ssobjectid,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            time_format = time_format,
            library = library,
            cache_data = cache_data
        )
    
    
    def single_light_curves(
        self,
        filters: list = FILTERS,
        title: str = None,
        cache_data: Optional[bool] = False
    ):
        filters = validate_filters(filters)
        
        plots = []

            
        for _filter in filters:
            lc = self.light_curve(
                filters = [_filter],
                title = title,
                cache_data = cache_data
            )
            plots.append(lc)
            
        return plots
    
    
    def plot_orbit(self,
                filters: Optional[list] = None,
                start_time : Optional[float] = None, end_time : Optional[float] = None,
                title : Optional[str] = None,
                projection: Optional[Literal['2d', '3d']] = '2d',
                library: Optional[str] = "seaborn",
                cache_data: Optional[bool] = False,
                ): 
        
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
        
        return _plot_orbit(
            df = df[['filter','heliocentricx', 'heliocentricy', 'heliocentricz']],
            #mpcdesignation = self.mpcdesignation,
            #ssobjectid = self.ssobjectid,
            filters = filters,
            start_time = start_time,
            end_time = end_time,
            title = title,
            projection = projection,
            library = library,
            cache_data = cache_data,
        )
    
    def clear(
        self,
        curve_df : Optional[bool] = True,
        orbit_df : Optional[bool] = True,
        
    ):
        if curve_df:
            self.curve_df = None
        if orbit_df:
            self.orbit_df = None
        
        return
        
    