import uuid
from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class SimulationModel(Base):
    __tablename__ = "TB_SIMULATIONS"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    iterationsNumber = Column(Integer)
    gridSize = Column(Integer)
    ingredients = Column(JSON)
    parameters = Column(JSON)