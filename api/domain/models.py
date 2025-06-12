import uuid
from typing import List

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

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
    results = Column(JSON)
    reactions = Column(JSON)
    rotation = Column(JSON)
    iterations: Mapped[List["IterationsModel"]] = relationship(
        "IterationsModel",
        cascade="all, delete-orphan",
    )


class IterationsModel(Base):
    __tablename__ = "TB_ITERATIONS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(
        UUID(as_uuid=True), ForeignKey("TB_SIMULATIONS.id"), nullable=False
    )
    chunk_number = Column(Integer, nullable=False)
    data = Column(Text, nullable=False)
