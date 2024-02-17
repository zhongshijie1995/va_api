from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from pydantic import BaseModel

from models.model_controller import Models


app = FastAPI()

scheduler = BackgroundScheduler()
models = Models()


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(func=Models.train, trigger='cron', second='*/30')
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


@app.get("/")
async def root():
    return {"message": "Hello World! This is va_api"}


class PredEntity(BaseModel):
    status: str = None
    detail: List = None
    name: str
    source: str
    mark: str = None


@app.post("/pred")
async def pred(pred_entity: PredEntity):
    try:
        pred_entity.status = '0000'
        pred_entity.detail, pred_entity.mark = models.pred(name=pred_entity.name, source=pred_entity.source)
    except Exception as e:
        pred_entity.status = '9999'
        pred_entity.detail = e.__str__()
    return pred_entity
