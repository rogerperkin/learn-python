from pydantic import BaseModel 
from typing import List

class Variant:(BaseModel)

class Product(BaseModel):
    id: int
    title: str
    variants: List[Variant]