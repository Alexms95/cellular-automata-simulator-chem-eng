from config import get_settings
from domain.schemas import IterationsResponse, SimulationCreate, SimulationResponse
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from logger import logger
from queries import SimulationData
from services.main_service import MainService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from utils import convert_to_csv

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Cellular Automata Calculator API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db)):
    return MainService(SimulationData(db))


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"Error not handled: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal Server Error"}
        )


@app.get("/simulations", response_model=list[SimulationResponse])
def get_simulations(service: MainService = Depends(get_service)):
    logger.info("Fetching all simulations")
    return service.get_simulations()


@app.post("/simulations", response_model=None)
def create_simulation(
    newSimulation: SimulationCreate, service: MainService = Depends(get_service)
):
    logger.info(f"Creating simulation: {newSimulation}")
    return service.create_simulation(newSimulation)


@app.put("/simulations/{id}", response_model=None)
def update_simulation(
    id: str,
    updatedSimulation: SimulationCreate,
    service: MainService = Depends(get_service),
):
    logger.info(f"Updating simulation with id {id}: {updatedSimulation}")
    return service.update_simulation(id, updatedSimulation)


@app.delete("/simulations/{id}", response_model=None)
def delete_simulation(id: str, service: MainService = Depends(get_service)):
    logger.info(f"Deleting simulation with id {id}")
    return service.delete_simulation(id)


@app.get("/simulations/{id}/run")
def run_simulation(id: str, service: MainService = Depends(get_service)):
    logger.info(f"Running simulation with id {id}")
    return StreamingResponse(
        service.run_simulation(id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/simulations/{id}", response_model=SimulationResponse)
def get_simulation(id: str, service: MainService = Depends(get_service)):
    logger.info(f"Fetching complete simulation with id {id}")
    return service.get_simulation(id)


@app.get(
    "/iterations/decompressed",
    response_model=list[list[list[int]]],
)
def get_decompressed_iterations(
    simulation_id: str,
    chunk_number: int = 0,
    service: MainService = Depends(get_service),
):
    logger.info(
        f"Fetching decompressed iterations for simulation with id {simulation_id} and chunk number {chunk_number}"
    )
    return service.get_decompressed_iterations(simulation_id, chunk_number)


@app.get("/simulations/{id}/results")
def get_results(
    id: str, service: MainService = Depends(get_service)
) -> StreamingResponse:
    logger.info(f"Downloading results for simulation with id {id}")

    name, results = service.get_results(id)

    csv_buffer = convert_to_csv(results)

    return StreamingResponse(
        iter([csv_buffer]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={name}.csv"},
    )


@app.get(
    "/iterations",
    response_model=IterationsResponse | None,
)
def get_iterations(
    simulation_id: str,
    chunk_number: int = 0,
    service: MainService = Depends(get_service),
):
    logger.info(
        f"Fetching iterations for simulation with id {simulation_id} and chunk number {chunk_number}"
    )
    return service.get_iterations_by_simulation(simulation_id, chunk_number)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
