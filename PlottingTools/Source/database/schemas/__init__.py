"""Schema defintion for the simulated LSST database. This is under active development"""


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from .dia_source import DIASource
from .mpcorb import MPCORB
from .ss_objects import SSObjects
from .ss_source import SSSource


diasource = DIASource.__table__
mpcorb = MPCORB.__table__
ssobjects = SSObjects.__table__
sssource = SSSource.__table__
