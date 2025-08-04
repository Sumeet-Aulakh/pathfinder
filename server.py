from typing import Union
from fastapi import FastAPI
from pathfinder import pathfinder

app = FastAPI()

@app.get("/current_document")
async def get_current_document():
    return pathfinder()


