from sqlalchemy import create_engine, text
from .db_config import DBConfig
import pandas as pd

class DB:
    def __init__(self, db_url : DBConfig.database_url):
        self.db_url = db_url
        
    def generate_connection(self):
        return create_engine(
            self.db_url
        ).connect()
    
    def get_tables(self):
        with self.generate_connection() as conn:
            results = conn.execution_options(
                postgresql_readonly = True # make this general? Not just postgres
            ).execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            return results
        
    #@cache
    def get_table_schema(self, table_name):        
        with self.generate_connection() as conn:
            results = conn.execution_options(
                postgresql_readonly = True
            ).execute(text(f"SELECT *  FROM information_schema.columns WHERE table_name='{table_name}'"))
            #COLUMN_NAME, DATA_TYPE, NUMERIC_PRECISION, CHARACTER_MAXIMUM_LENGTH, COLUMN_DEFAULT
            return results
    
    def query(self, stmt, return_as_df: bool = True): # option to return as SQLAlchemy cursor or pandas dataframe.
        with self.generate_connection() as conn:
            if return_as_df:
                results = pd.read_sql(stmt, conn)
            else: # return sql_cursor
                results = conn.execution_options(
                    postgresql_readonly = True
                ).execute(stmt)
        return results
    
    def transaction(self, stmts: list):
        results = []
        with self.generate_connection() as conn:
            for stmt in stmts:
                results.append(pd.read_sql(stmt, conn))
        return results