from . import Base
from sqlalchemy import Column, VARCHAR, Integer, DateTime, Float, BigInteger, ForeignKey

class MPCORB(Base):
    __tablename__ = "mpcorb"

    mpcdesignation = Column(VARCHAR(8), primary_key=True)
    mpcnumber = Column(Integer)
    ssobjectid = Column(BigInteger, ForeignKey("ssobjects.ssobjectid")) # secondary key - 
    mpch = Column(Float)
    mpcg = Column(Float)
    epoch = Column(Float)
    #a = Column(Float(2))
    q = Column(Float(2))
    m = Column(Float(2))
    peri = Column(Float(2))
    node = Column(Float(2))
    incl = Column(Float(2))
    e = Column(Float(2))
    n = Column(Float(2))
    uncertaintyparameter = Column(VARCHAR(1))
    reference = Column(VARCHAR(9))
    nobs = Column(Integer)
    nopp = Column(Integer)
    arc = Column(Float)
    arcstart = Column(DateTime)
    arcend = Column(DateTime)
    rms = Column(Float)
    pertsshort = Column(VARCHAR(3))
    pertslong = Column(VARCHAR(3))
    computer = Column(VARCHAR(10))
    flags = Column(Integer)
    fulldesignation = Column(VARCHAR(26))
    lastincludedObservation = Column(Float)
    covariance = Column(Float(21))