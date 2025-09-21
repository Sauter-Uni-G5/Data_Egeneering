from fastapi import FastAPI
from app.controllers import ear_controller, hydro_controller, weather_controller, registry_controller

app = FastAPI(
    title="ONS Data API", 
    version="1.0.0",
    description="API para acessar dados do ONS (Operador Nacional do Sistema Elétrico)"
)

app.include_router(ear_controller.router, prefix="/api", tags=["EAR - Energia Armazenada"])
app.include_router(hydro_controller.router, prefix="/api", tags=["Hydro - Dados Hidráulicos"])
app.include_router(weather_controller.router, prefix="/api", tags=["Weather - Meteorologia"])
app.include_router(registry_controller.router, prefix="/api", tags=["Registry - Reservoir Registry"])

@app.get("/")
def read_root():
    return {
        "message": "ONS Data API is running",
        "endpoints": {
            "ear": "/api/data/ear",
            "hydro": "/api/data/hydro"
        },
        "example_usage": {
            "ear_with_dates": "/api/data/ear?package_id=61e92787-9847-4731-8b73-e878eb5bc158&start_date=2022-05-10&end_date=2023-09-30&page=1&page_size=50",
            "hydro_with_year": "/api/data/hydro?package_id=seu-package-id&ano=2023&mes=5&page=1&page_size=100"
        }
    }