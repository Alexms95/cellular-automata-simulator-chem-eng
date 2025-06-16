from datetime import datetime
from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    molarFraction: float
    color: str


class PairParameter(BaseModel):
    relation: str
    value: float


class Parameters(BaseModel):
    Pm: list[float]
    J: list[PairParameter]


class Reaction(BaseModel):
    reactants: list[str]
    products: list[str]
    Pr: list[float]
    reversePr: list[float]
    hasIntermediate: bool


class Rotation(BaseModel):
    component: str
    Prot: float


class SimulationBase(BaseModel):
    name: str
    iterationsNumber: int
    gridLenght: int
    gridHeight: int
    ingredients: list[Ingredient]
    parameters: Parameters
    reactions: list[Reaction] | None
    rotation: Rotation


class SimulationCreate(SimulationBase):
    pass


class SimulationResponse(SimulationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RotationInfo(TypedDict):
    component: int
    p_rot: float
    states: list[int]


class IterationsResponse(BaseModel):
    simulation_id: UUID
    chunk_number: int
    data: str

    class Config:
        from_attributes = True
