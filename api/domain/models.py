import uuid
from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class SimulationModel(Base):
    __tablename__ = "TB_SIMULATIONS"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False, unique=True)
    iterationsNumber = Column(Integer, nullable=False)
    gridLenght = Column(Integer, nullable=False)
    gridHeight = Column(Integer, nullable=False)
    ingredients = Column(JSON, nullable=False)
    parameters = Column(JSON, nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    iterations = Column(Text)
    results = Column(JSON)
    reactions = Column(JSON)
    rotation = Column(JSON)
