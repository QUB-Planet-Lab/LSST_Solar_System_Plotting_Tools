#!/usr/bin/env python
# coding: utf-8

# # This is a Python File that will communicate with the LSST Solar System Simulated PostgreSQL Database

import psycopg2 as pg
import pandas as pd
import numpy as np

import sys

from sqlalchemy import create_engine
from database import DBConfig



##
## create_connection_and_queryDB : This function allows connection to the database.
## cmd : This refers to the sql command that will be executed on the database. (string)
## parameters : these are values for some of the constraints on some of the columns within the tables, it is usually in the form of a dictionary
def create_connection_and_queryDB(cmd,parameters):
    try: 
        #Access the database password and bring it into memory
        with open("/home/shared/sssc-db-pass.txt") as pwf:
            pwd = pwf.read()
        # this with also automatically closes the reading of the password file.
    except:
        print('Error in accessing database password')
    try:
        # uses the pyscopg2 module to open a connection to the postgreSQL database using the password, 5432 is the typical port to use.
        
        db_url = DBConfig(password = pwd,
                          user = 'sssc',
                          port = '5432',
                          db_name = 'lsst_solsys',
                          dialect = 'postgresql',
                          driver ='psycopg2',
                          host = 'epyc.astro.washington.edu'
                         ).database_url
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            return pd.read_sql(cmd, conn, params = parameters)
        
        # the sql command and the open connection string and the parameters are sent to the database, the database then handles the parameters themselves and treats those values
        # as values which removes issues such as sql injection from being executed.
        # connection to the database is then closed once the data is received from the database.
        # the results dataframe is then returned to the function that called this function.
        
    except Exception as ex:  
        ## If there is an issue then perform a system exit as this means there is something critically wrong and no use executing anymore code.
        print('Error in reading from the database')
        sys.exit()
