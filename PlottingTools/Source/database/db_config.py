from dataclasses import dataclass
#from typing import Literal, Optional 

@dataclass
class DBConfig:
    """
    :param user: str
    :param port: str
    """
    user : str
    port : str
    db_name : str
    host: str
    password : str
    dialect : str#Literal['postgresql', 'mysql', 'sqlite3']
    driver : str #Optional[Literal['psycopg2', '']] = ''
    
    
    @property
    def database_url(self) -> str: # change dialect
        """ database url
        :return: str
        """
        return f"{self.dialect}+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
    
    


