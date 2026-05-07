from pydantic import BaseModel
from typing import Optional

class LugarCreate(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    fuente: Optional[str] = "manual"

class LugarUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None