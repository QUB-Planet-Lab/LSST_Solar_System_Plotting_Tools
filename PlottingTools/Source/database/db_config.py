from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class DBConfig:
    user : str
    port : str
    db_name : str
    host: str
    password : str
    dialect : Literal['postgresql', 'mysql', 'sqlite3']
    driver : Optional[Literal['psycopg2', '']] = ''
    
    
    @property
    def database_url(self): # change dialect
        return f"{self.dialect}+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
    
    


