from pydantic import BaseModel
from typing import Optional


class ObjectRead(BaseModel):
    uuid: str
    name: str
    description: Optional[str] = None


class ObjectWrite(BaseModel):
    name: str
    description: Optional[str] = None
