from dataclasses import dataclass
from typing import List, Optional
from .grupo_dto import GrupoDTO

@dataclass
class MateriaDTO:
    """Data Transfer Object para una Materia."""
    codigo: str
    nombre: str
    creditos: int
    grupos: List[GrupoDTO]
    color: Optional[str] = None # For UI purposes
