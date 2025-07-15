from pydantic import BaseModel, Field
from typing import Optional


class ObjectRead(BaseModel):
    uuid: str
    name: str
    description: Optional[str] = None
    created_by: Optional[str] = Field(None, description="User who created the object")


class ObjectWrite(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: Optional[str] = Field(None, description="User who created the object")
