from fastapi import FastAPI
from app.controllers import ear_controller, hydro_controller, upload_controller, weather_controller, registry_controller
from app.controllers import pipeline_controller

app = FastAPI(title="Sauter University Data Engineering API")

app.include_router(weather_controller.router, prefix="/api")
app.include_router(hydro_controller.router, prefix="/api")
app.include_router(ear_controller.router, prefix="/api")
app.include_router(registry_controller.router, prefix="/api")
app.include_router(upload_controller.router, prefix="/api")
app.include_router(pipeline_controller.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "API is running"}