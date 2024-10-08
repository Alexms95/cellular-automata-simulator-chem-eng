from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.views.calculation_view import router as calculation_router
from app.views.simulation_view import router as simulation_router

app = FastAPI(title="Cellular Automata Calculator API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculation_router, prefix="/calculate", tags=["calculation"])
app.include_router(simulation_router, prefix="/simulations", tags=["Simulations"])

@app.get("/")
def read_root():
    return {"Hello": "World"}