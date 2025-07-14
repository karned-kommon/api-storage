from pydantic import BaseModel
from typing import Optional

class StorageRead(BaseModel):
    uuid: str
    name: str
    description: Optional[str] = None

class StorageWrite(BaseModel):
    name: str
    description: Optional[str] = None
