from dataclasses import dataclass
from typing import Optional

@dataclass
class SesionDTO:
    """Data Transfer Object para una Sesión de Clase."""
    id: Optional[int]
    dia: str
    hora_inicio: str
    hora_fin: str
    salon: str
    docente: str
    tipo: str
