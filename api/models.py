from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SimulationModel(Base):
    __tablename__ = "tb_simulations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    iterationsNumber = Column(Integer)
    gridDimension = Column(Integer)
    ingredients = Column(JSON)
    parameters = Column(JSON)