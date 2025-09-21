import logging
from fastapi import FastAPI
from app.controllers import ear_controller

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

app.include_router(ear_controller.router)
