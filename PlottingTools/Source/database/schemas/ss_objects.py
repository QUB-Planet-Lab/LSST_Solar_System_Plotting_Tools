"""Schema for SSObjects"""
from . import Base
from sqlalchemy import Column, Integer, Float #, BLOB

class SSObjects(Base):
    __tablename__ = "ssobjects"
    
    
    ssobjectid = Column(Integer, primary_key=True) #Unique identifier.
    discoverysubmissiondate = Column(Float) 
    firstobservationdate = Column(Float) 
    arc= Column(Float) 
    numobs = Column(Integer)
    #lcperiodic = Column(BLOB) # need to figure out how to put blob
    moid = Column(Float)
    moidtrueanomaly = Column(Float)
    moideclipticlongitude = Column(Float)
    moiddeltav = Column(Float)
    uh = Column(Float)
    ug12 = Column(Float)
    uherr = Column(Float)
    ug12err = Column(Float)
    uh = Column(Float)
    uh_ug12_cov = Column(Float)
    uchi2 = Column(Float)
    undata = Column(Integer)
    gh = Column(Float)
    gg12 = Column(Float)
    gherr = Column(Float)
    gg12err = Column(Float)
    gh_gg12_cov = Column(Float)
    gchi2 = Column(Float)
    gndata = Column(Integer)
    rh = Column(Float)
    rg12 = Column(Float)
    rherr = Column(Float)
    rg12err = Column(Float)
    rh_rg12_cov = Column(Float)
    rchi2 = Column(Float)
    rndata = Column(Integer)
    ih = Column(Float)
    ig12 = Column(Float)
    iherr = Column(Float)
    ig12err = Column(Float)
    ih_ig12_cov = Column(Float)
    ichi2 = Column(Float)
    indata = Column(Integer)
    zh = Column(Float)
    zg12 = Column(Float)
    zherr = Column(Float)
    zg12err = Column(Float)
    zh_zg12_cov = Column(Float)
    zchi2 = Column(Float)
    zndata = Column(Integer)
    yh = Column(Float)
    yg12 = Column(Float)
    yherr = Column(Float)
    yg12err = Column(Float)
    yh_yg12_cov = Column(Float)
    ychi2 = Column(Float)
    yndata = Column(Integer)
    maxextendedness = Column(Float)
    minextendedness = Column(Float)
    medianextendedness = Column(Float)
    flags = Column(Integer)
