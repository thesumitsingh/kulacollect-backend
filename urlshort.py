from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    uniqueid: int
    