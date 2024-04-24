from typing import Union
import audit_download
from fastapi import FastAPI
# from pydantic import BaseModel
app = FastAPI()



@app.get("/audit")
def audit(netid: str, password: str):
    return audit_download.get_audit(netid, password)

@app.get("/")
def read_root():
    return {"Hello": "World"}