"""
database module deals with connections and transactions to the the database.
"""

from .db_config import DBConfig
from .db import DB



try:
    with open("/home/shared/sssc-db-pass.txt") as pwf:
        pwd = pwf.read()

except:
    print("Error accessing the pwd file")
try:
    db_url = DBConfig(password = pwd,
                      user = 'sssc',
                      port = '5432',
                      db_name = 'lsst_solsys',
                      dialect = 'postgresql',
                      driver ='psycopg2',
                      host = 'epyc.astro.washington.edu'
                     ).database_url
    db = DB(db_url = db_url)
    
except:
    db = None
    print("Cannot create db_url")
    



    