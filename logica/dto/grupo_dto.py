from dataclasses import dataclass
from typing import List, Optional
from .sesion_dto import SesionDTO

@dataclass
class GrupoDTO:
    """Data Transfer Object para un Grupo de Materia."""
    id: Optional[int]
    nombre: str
    cupos: int
    sesiones: List[SesionDTO]
