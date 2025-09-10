"""
Modelos de datos para el sistema de horarios
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import time

@dataclass
class Materia:
    """Modelo de datos para una materia"""
    codigo_materia: str
    nombre_materia: str
    creditos: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones automáticas después de la inicialización"""
        if not self.codigo_materia.strip():
            raise ValueError("El código de materia no puede estar vacío")
        if not self.nombre_materia.strip():
            raise ValueError("El nombre de materia no puede estar vacío")
        if self.creditos is not None and self.creditos < 0:
            raise ValueError("Los créditos no pueden ser negativos")

@dataclass
class GrupoMateria:
    """Modelo de datos para un grupo de materia"""
    id_grupo_materia: Optional[int] = None
    codigo_materia_fk: str = ""
    nombre_grupo: str = ""
    cupos: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones automáticas después de la inicialización"""
        if not self.codigo_materia_fk.strip():
            raise ValueError("El código de materia FK no puede estar vacío")
        if not self.nombre_grupo.strip():
            raise ValueError("El nombre del grupo no puede estar vacío")
        if self.cupos is not None and self.cupos < 0:
            raise ValueError("Los cupos no pueden ser negativos")

@dataclass
class SesionClase:
    """Modelo de datos para una sesión de clase"""
    id_sesion: Optional[int] = None
    id_grupo_materia_fk: Optional[int] = None
    tipo_sesion: str = ""
    dia_semana: str = ""
    hora_inicio: str = ""
    hora_fin: str = ""
    docente: Optional[str] = None
    salon: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones automáticas después de la inicialización"""
        if not self.tipo_sesion.strip():
            raise ValueError("El tipo de sesión no puede estar vacío")
        if not self.dia_semana.strip():
            raise ValueError("El día de la semana no puede estar vacío")
        if not self.hora_inicio.strip():
            raise ValueError("La hora de inicio no puede estar vacía")
        if not self.hora_fin.strip():
            raise ValueError("La hora de fin no puede estar vacía")
        
        # Validar formato de horas
        self._validar_formato_hora(self.hora_inicio)
        self._validar_formato_hora(self.hora_fin)
    
    def _validar_formato_hora(self, hora_str: str):
        """Valida que una hora tenga el formato correcto HH:MM"""
        try:
            parts = hora_str.split(':')
            if len(parts) != 2:
                raise ValueError()
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError()
        except (ValueError, IndexError):
            raise ValueError(f"Formato de hora inválido: {hora_str}. Use HH:MM")

@dataclass
class MateriaCompleta:
    """Modelo completo de una materia con sus grupos y sesiones"""
    materia: Materia
    grupos: List['GrupoCompleto']
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MateriaCompleta':
        """Crea una instancia desde un diccionario"""
        materia = Materia(
            codigo_materia=data['codigo'],
            nombre_materia=data['nombre'],
            creditos=data.get('creditos')
        )
        
        grupos = []
        for grupo_data in data.get('grupos_materia', []):
            grupo = GrupoCompleto.from_dict(grupo_data)
            grupos.append(grupo)
        
        return cls(materia=materia, grupos=grupos)

@dataclass
class GrupoCompleto:
    """Modelo completo de un grupo con sus sesiones"""
    grupo: GrupoMateria
    sesiones: List[SesionClase]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GrupoCompleto':
        """Crea una instancia desde un diccionario"""
        grupo = GrupoMateria(
            id_grupo_materia=data.get('id_db_grupo'),
            codigo_materia_fk=data.get('codigo_materia_fk', ''),
            nombre_grupo=data.get('nombre_grupo_original', ''),
            cupos=data.get('cupos')
        )
        
        sesiones = []
        for sesion_data in data.get('sesiones', []):
            sesion = SesionClase(
                id_sesion=sesion_data.get('id_db_sesion'),
                id_grupo_materia_fk=grupo.id_grupo_materia,
                tipo_sesion=sesion_data.get('tipo', ''),
                dia_semana=sesion_data.get('dia', ''),
                hora_inicio=sesion_data.get('hora_inicio', ''),
                hora_fin=sesion_data.get('hora_fin', ''),
                docente=sesion_data.get('docente'),
                salon=sesion_data.get('salon')
            )
            sesiones.append(sesion)
        
        return cls(grupo=grupo, sesiones=sesiones)

@dataclass
class HorarioAsignado:
    """Modelo para un horario asignado en la grilla"""
    materia: Materia
    grupo: GrupoMateria
    sesion: SesionClase
    dia: str
    hora: str
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para compatibilidad con el código existente"""
        return {
            'codigo': self.materia.codigo_materia,
            'info': {
                'nombre': self.materia.nombre_materia,
                'creditos': self.materia.creditos or 0
            },
            'nombre_grupo': self.grupo.nombre_grupo,
            'horario_sesion': {
                'dia_semana': self.sesion.dia_semana,
                'hora_inicio': self.sesion.hora_inicio,
                'hora_fin': self.sesion.hora_fin,
                'tipo_sesion': self.sesion.tipo_sesion,
                'docente': self.sesion.docente,
                'salon': self.sesion.salon
            }
        }
        
print("Test finalizado correctamente.")
