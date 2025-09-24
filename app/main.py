from fastapi import FastAPI
from app.controllers import (
    ear_controller, 
    hydro_controller, 
    weather_controller, 
    registry_controller,
    pipeline_controller
)

app = FastAPI(
    title="Data Engineering API",
    description="API para processamento de dados de reservatórios",
    version="1.0.0"
)

# Incluir os routers
app.include_router(ear_controller.router, prefix="/api", tags=["EAR"])
app.include_router(hydro_controller.router, prefix="/api", tags=["Hydro"])
app.include_router(weather_controller.router, prefix="/api", tags=["Weather"])
app.include_router(registry_controller.router, prefix="/api", tags=["Registry"])
app.include_router(pipeline_controller.router, prefix="/api", tags=["Pipeline"])

@app.get("/")
def read_root():
    return {"message": "API is running"}