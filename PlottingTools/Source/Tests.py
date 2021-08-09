#!/usr/bin/env python
# coding: utf-8

# In[19]:
import os

s_path = os.getcwd()
print(s_path)
import unittest
import psycopg2 as pg
from Functions import VariableTesting,DateorMJD
from Plots import *
import pandas as ps
import numpy as np
from astropy.time import Time

# class TestDB(unittest.TestCase):

#     def test_DBconnection(self):
#         """
#         Test to ensure the query through DAL gives same result as a query done in the test.
#         """
#         with open("/home/shared/sssc-db-pass.txt") as pwf:
#             pwd = pwf.read()
#         connectionstring = pg.connect(database="lsst_solsys", user="sssc", password=pwd, host="epyc.astro.washington.edu", port="5432")
#         ps.testing.assert_frame_equal(ps.read_sql("SELECT * FROM mpcorb LIMIT 5",connectionstring,params = dict()) ,dal.create_connection_and_queryDB("SELECT * FROM mpcorb LIMIT 5",dict()))
        
class TestFunc(unittest.TestCase):
    
    def test_variable_testing(self):
        VariableTesting(0,2,60042,None,None,None,Time.now(),-7)

class Test_Hist(unittest.TestCase):
    theframe = ps.read_csv(s_path+'/Cache/iqeaframe-q-5.csv',nrows=100)
#     def test_24hist(self):
        
#         Weekly24hrHist(0,2,60042,ShowPlot=False)
    def test_ieqa2dHist_9(self):
        self.assertIsNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=False,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['a','incl','inclination-semimajor'],xylabels=['semimajor axis (au)','inclination (degrees)']))
    
    def test_ieqa2dHist_8(self):
        self.assertIsNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=False,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity']))
         
    def test_ieqa2dHist_7(self):
        self.assertIsNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=False,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',]))
         
    def test_ieqa2dHist_6(self):
        self.assertIsNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=False,DataFrame=Test_Hist.theframe,ShowPlot=False))
         
    def test_ieqa2dHist_5(self):
        self.assertIsNotNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=True,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['a','incl','inclination-semimajor'],xylabels=['semimajor axis (au)','inclination (degrees)']))

         
    def test_ieqa2dHist_4(self):
        self.assertIsNotNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=True,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity']))
         
    def test_ieqa2dHist_3(self):
        self.assertIsNotNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=True,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',]))
         
    def test_ieqa2dHist_2(self):
        self.assertIsNotNone(iqeaHistogramPlot2D(60042,a_min=27,a_max=80,KeepData=True,DataFrame=Test_Hist.theframe,ShowPlot=False,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',]))

    def test_ieqa2dHist_1(self):
        
         """
         Test to ensure each of these remain valid within the program.
         """
         self.assertIsNotNone(Test_Hist.theframe)
         
    def test_ieqahexplot_10(self):
        self.assertIsNotNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=True,DataFrame=Test_Hist.theframe))   
         
    def test_ieqahexplot_9(self):
        self.assertIsNotNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=True,DataFrame=Test_Hist.theframe,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',]))
         
    def test_ieqahexplot_8(self):
        self.assertIsNotNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=True,DataFrame=Test_Hist.theframe,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity']))
         
    def test_ieqahexplot_7(self):
        self.assertIsNotNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=True,DataFrame=Test_Hist.theframe,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity']))
         
    def test_ieqahexplot_6(self):
        self.assertIsNotNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=True,DataFrame=Test_Hist.theframe,xyscale=['a','incl','inclination-semimajor'],xylabels=['semimajor axis (au)','inclination (degrees)']))

    def test_ieqahexplot_5(self):
        self.assertIsNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=False,DataFrame=Test_Hist.theframe))
         
    def test_ieqahexplot_4(self):
        self.assertIsNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=False,DataFrame=Test_Hist.theframe,xyscale=['q','incl','inclination-perhelion'],xylabels=['perihelion (au)','inclination (degrees)',]))
         
    def test_ieqahexplot_3(self):
        self.assertIsNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=False,DataFrame=Test_Hist.theframe,xyscale=['a','e','eccentricity-semimajor'],xylabels=['semimajor axis (au)','eccentricity']))
         
    def test_ieqahexplot_2(self):
        self.assertIsNone(iqeaHexPlot(60042,a_min=27,a_max=80,ShowPlot=False,KeepData=False,DataFrame=Test_Hist.theframe,xyscale=['a','incl','inclination-semimajor'],xylabels=['semimajor axis (au)','inclination (degrees)']))

    def test_ieqahexplot_1(self):
         """
         Test to ensure each of these remain valid within the program.
         """
         
         self.assertIsNotNone(Test_Hist.theframe)
         
         
    
    
    
    
#     def test_helio_dist_hist(self):
#         self.assertIsNotNone(HelioDistHist(60042,DateInterval = 4,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3]],KeepData=True,ShowPlot=False))
#         self.assertIsNotNone(HelioDistHist(60042,DateInterval = 2,KeepData=True,ShowPlot=False))
        
        
#         self.assertIsNone(HelioDistHist(60042,DateInterval = 4,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3]],ShowPlot=False))
        
#         self.assertIsNone(HelioDistHist(60042,DateInterval = 4,DistanceMinMax=[[1.5,2],[2,2.5],[2.5,3]],ShowPlot=False))
        
        
        
        
        
    
class TestDF(unittest.TestCase):

    CDF = ps.read_csv('./Cache/CDF.csv',nrows=100)
    CDF2 = ps.read_csv('./Cache/CDF2.csv',nrows=100)
    CDF3 = ps.read_csv('./Cache/CDF3.csv',nrows=100)
    dataframe =ps.read_csv('./Cache/bev_cache',nrows=100)
    violin = ps.read_csv('./Cache/violin_cache', nrows=100)
    date = 60042.75
#     def test_check_no_default_exceptions(self):
#         run_plot_defaults(True,True,True,date = 60042,NightBefore=False,ShowPlot=False)
    
   
    
    
    
    def test_immutabledata_15(self):
        ps.testing.assert_frame_equal(TestDF.CDF2,boxwhisker_plot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF2,KeepData=True,ShowPlot=False,boxOrBoxen=2))
    def test_immutabledata_14(self):
        ps.testing.assert_frame_equal(TestDF.CDF2,boxwhisker_plot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF2,KeepData=True,ShowPlot=False,boxOrBoxen=1))
    def test_immutabledata_13(self):
        ps.testing.assert_frame_equal(TestDF.CDF2,boxwhisker_plot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF2,KeepData=True,ShowPlot=False,boxOrBoxen=0))

        
    def test_immutabledata_12(self):
        ps.testing.assert_frame_equal(TestDF.CDF,Heliocentric_HexPlot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF,KeepData=True,ShowPlot=False))
    def test_immutabledata_11(self):
        ps.testing.assert_frame_equal(TestDF.CDF3,Topocentric_HexPlot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF3,KeepData=True,ShowPlot=False))
        
    def test_immutabledata_10(self):
        ps.testing.assert_frame_equal(TestDF.CDF,Heliocentric_HexPlot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF,KeepData=True,ShowPlot=False,Filters = 'grizy'))
        
    def test_immutabledata_9(self):
        ps.testing.assert_frame_equal(TestDF.CDF3,Topocentric_HexPlot(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF3,KeepData=True,ShowPlot=False,Filters = 'grizy'))

    def test_immutabledata_8(self):
        ps.testing.assert_frame_equal(TestDF.CDF3,Topocentric_HistogramPlot2D(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF3,KeepData=True,ShowPlot=False,Filters = 'grizy'))


    def test_immutabledata_7(self):
        ps.testing.assert_frame_equal(TestDF.CDF,Heliocentric_HistogramPlot2D(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF,KeepData=True,ShowPlot=False,Filters = 'grizy'))
        
    def test_immutabledata_6(self):
        ps.testing.assert_frame_equal(TestDF.CDF3,Topocentric_HistogramPlot2D(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF3,KeepData=True,ShowPlot=False))
        
    def test_immutabledata_5(self):
        ps.testing.assert_frame_equal(TestDF.CDF,Heliocentric_HistogramPlot2D(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF,KeepData=True,ShowPlot=False))
        
    def test_immutabledata_4(self):
        ps.testing.assert_frame_equal(TestDF.CDF3,Topocentric_BirdsEyeView(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF3,KeepData=True,ShowPlot=False,Filters = 'grizy'))

    def test_immutabledata_3(self):
        ps.testing.assert_frame_equal(TestDF.CDF,Heliocentric_BirdsEyeView(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF,KeepData=True,ShowPlot=False,Filters = 'grizy'))
    def test_immutabledata_2(self):
        ps.testing.assert_frame_equal(TestDF.CDF3,Topocentric_BirdsEyeView(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF3,KeepData=True,ShowPlot=False))
        
    def test_immutabledata_1(self):
        ps.testing.assert_frame_equal(TestDF.CDF,Heliocentric_BirdsEyeView(0,2,TestDF.date,filename='test',title = None,DataFrame=TestDF.CDF,KeepData=True,ShowPlot=False))
            
    
    def test_violin_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042 
        self.assertIsNotNone(violin_plot(0,2,date,filename='test',title = None,KeepData=True,ShowPlot=False,DataFrame=TestDF.violin))
        
    def test_violin_not_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042  
        self.assertIsNone(violin_plot(0,2,date,filename='test',title = None,KeepData=False,ShowPlot=False,DataFrame=TestDF.violin))
    
    def test_hexplot_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042

        self.assertIsNotNone(HexPlot(0,2,date,filename='test',title = None,KeepData=True,ShowPlot=False,DataFrame=TestDF.dataframe))
        
    def test_hexplot_not_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042  
        self.assertIsNone(HexPlot(0,2,date,filename='test',title = None,KeepData=False,ShowPlot=False,DataFrame=TestDF.dataframe))
    
    def test_hist2d_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042  
        self.assertIsNotNone(HistogramPlot2D(0,2,date,filename='test',title = None,KeepData=True,ShowPlot=False,DataFrame=TestDF.dataframe))
        
    def test_hist2d_not_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042  
        self.assertIsNone(HistogramPlot2D(0,2,date,filename='test',title = None,KeepData=False,ShowPlot=False,DataFrame=TestDF.dataframe))
    
    def test_bev_return_df(self):
        """
        Test That when KeepData = True a Database is returned.
        """
        date = 60042
        #dataframe =ps.read_csv('./Cache/bev_cache',nrows=1000)
        self.assertIsNotNone(BirdsEyeViewPlotter(0,2,date,filename='test',title = None,KeepData=True,ShowPlot=False,DataFrame=TestDF.dataframe))
        #self.assertIsNotNone(BirdsEyeViewPlotter(6,25,date,filename='test',title = None,KeepData=True,ShowPlot=False))
        #self.assertIsNotNone(BirdsEyeViewPlotter(2,6,date,filename='test',title = None,KeepData=True,ShowPlot=False))
        #self.assertIsNotNone(BirdsEyeViewPlotter(25,100,date,filename='test',title = None,KeepData=True,ShowPlot=False))
    
        
    def test_bev_not_return_df(self):
        """
        Test That when KeepData = False a Database is not returned.
        """
        date = 60042
        #dataframe =ps.read_csv('./Cache/bev_cache',nrows=1000)
        self.assertIsNone(BirdsEyeViewPlotter(0,2,date,filename='test',title = None,KeepData=False,ShowPlot=False,DataFrame=TestDF.dataframe))
        #self.assertIsNone(BirdsEyeViewPlotter(6,25,date,filename='test',title = None,KeepData=False,ShowPlot=False))
        #self.assertIsNone(BirdsEyeViewPlotter(2,6,date,filename='test',title = None,KeepData=False,ShowPlot=False))
        #self.assertIsNone(BirdsEyeViewPlotter(25,100,date,filename='test',title = None,KeepData=False,ShowPlot=False))

if __name__ == '__main__':        
    unittest.main(argv=['M87'], exit=False)

