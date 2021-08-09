#!/usr/bin/env python
# coding: utf-8

# # This is a Python File that will communicate with the LSST Solar System Simulated PostgreSQL Database

# In[1]:


#psycopg2 : used to communicate with the database
import psycopg2 as pg
#Pandas: be used for dataframes and other useful file manipulations
import pandas as pd
# NumPy : Useful for arrays and array operations, and much more versatile than built in python arrays and lists.
import numpy as np

import sys

# In[2]:


##
## connectionstring = pg.connect(database="lsst_solsys", user="sssc", password=pwd, host="epyc.astro.washington.edu", port="5432")
##
def create_connection_and_queryDB(cmd,parameters):
    print(type(parameters),parameters)
    try: 
        #Access the database password and bring it into memory
        with open("/home/shared/sssc-db-pass.txt") as pwf:
            pwd = pwf.read()
 
    except:
        print('Error in accessing database password')
    try:

        connectionstring = pg.connect(database="lsst_solsys", user="sssc", password=pwd, host="epyc.astro.washington.edu", port="5432")
        df = pd.read_sql(cmd, connectionstring,params = parameters)
        connectionstring.close()
        return df
    except Exception as ex:  
        ## Make this sys exit.
        print('Error in reading from the database')
        sys.exit()