from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from queries import SimulationData

from config import get_settings
from schemas import SimulationCreate, SimulationResponse

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Cellular Automata Calculator API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/simulations", response_model=list[SimulationResponse])
def get_simulations(dataAccess: SimulationData = Depends(), db: Session = Depends(get_db)):
    return dataAccess.get_simulations(db)

@app.post("/simulations", response_model=None)
def create_simulation(newSimulation: SimulationCreate, dataAccess: SimulationData = Depends(), db: Session = Depends(get_db)):
    return dataAccess.create_simulation(newSimulation, db)

@app.get("/")
def read_root():
    return {"Hello": "World"}