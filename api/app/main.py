from fastapi import FastAPI

from app.views.calculation_view import router as calculation_router

app = FastAPI(title="Calculator API")

app.include_router(calculation_router, prefix="/calculate", tags=["calculation"])

@app.get("/")
def read_root():
    return {"Hello": "World"}