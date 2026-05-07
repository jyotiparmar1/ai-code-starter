from pydantic import BaseModel
from typing import List

class Field(BaseModel):
    name: str
    type: str

class Entity(BaseModel):
    name: str
    fields: List[Field]

class API(BaseModel):
    endpoint: str
    method: str

class ProjectSpec(BaseModel):
    entities: List[Entity]
    apis: List[API]