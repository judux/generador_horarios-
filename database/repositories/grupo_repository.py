"""
Repositorio para la tabla GruposMateria
"""

import logging
from typing import List, Optional, Dict, Any
from database.connection import DatabaseManager
from database.models import GrupoMateria

logger = logging.getLogger(__name__)

class GrupoRepository:
    """Repositorio para interactuar con la tabla GruposMateria"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def crear(self, grupo: GrupoMateria) -> bool:
        """Crea un nuevo grupo de materia"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO GruposMateria (codigo_materia_fk, nombre_grupo, cupos) VALUES (?, ?, ?)",
                    (grupo.codigo_materia_fk, grupo.nombre_grupo, grupo.cupos)
                )
            return True
        except Exception as e:
            logger.error(f"Error creando grupo: {e}")
            return False
    
    def obtener_por_id(self, id_grupo: int) -> Optional[GrupoMateria]:
        """Obtiene un grupo por su ID"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute("SELECT * FROM GruposMateria WHERE id_grupo_materia = ?", (id_grupo,))
                row = cursor.fetchone()
                if row:
                    return GrupoMateria(id_grupo_materia=row[0], codigo_materia_fk=row[1], nombre_grupo=row[2], cupos=row[3])
            return None
        except Exception as e:
            logger.error(f"Error obteniendo grupo por ID {id_grupo}: {e}")
            return None
    
    def obtener_por_materia(self, codigo_materia: str) -> List[GrupoMateria]:
        """Obtiene todos los grupos de una materia"""
        grupos = []
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute("SELECT * FROM GruposMateria WHERE codigo_materia_fk = ?", (codigo_materia,))
                rows = cursor.fetchall()
                for row in rows:
                    grupos.append(GrupoMateria(id_grupo_materia=row[0], codigo_materia_fk=row[1], nombre_grupo=row[2], cupos=row[3]))
        except Exception as e:
            logger.error(f"Error obteniendo grupos para materia {codigo_materia}: {e}")
        return grupos

    def obtener_por_materia_y_nombre(self, codigo_materia: str, nombre_grupo: str) -> Optional[GrupoMateria]:
        """Obtiene un grupo específico por materia y nombre"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM GruposMateria WHERE codigo_materia_fk = ? AND nombre_grupo = ?",
                    (codigo_materia, nombre_grupo)
                )
                row = cursor.fetchone()
                if row:
                    return GrupoMateria(id_grupo_materia=row[0], codigo_materia_fk=row[1], nombre_grupo=row[2], cupos=row[3])
            return None
        except Exception as e:
            logger.error(f"Error obteniendo grupo '{nombre_grupo}' para materia {codigo_materia}: {e}")
            return None

    def actualizar(self, grupo: GrupoMateria) -> bool:
        """Actualiza un grupo existente"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute(
                    "UPDATE GruposMateria SET nombre_grupo = ?, cupos = ? WHERE id_grupo_materia = ?",
                    (grupo.nombre_grupo, grupo.cupos, grupo.id_grupo_materia)
                )
            return True
        except Exception as e:
            logger.error(f"Error actualizando grupo {grupo.id_grupo_materia}: {e}")
            return False
    
    def eliminar(self, id_grupo: int) -> bool:
        """Elimina un grupo por su ID"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute("DELETE FROM GruposMateria WHERE id_grupo_materia = ?", (id_grupo,))
            return True
        except Exception as e:
            logger.error(f"Error eliminando grupo {id_grupo}: {e}")
            return False

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas sobre los grupos"""
        try:
            with self.db_manager.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM GruposMateria")
                total_grupos = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(c) FROM (SELECT COUNT(*) as c FROM GruposMateria GROUP BY codigo_materia_fk)")
                avg_grupos_por_materia = cursor.fetchone()[0]
                
                return {
                    'total_grupos': total_grupos,
                    'promedio_grupos_por_materia': round(avg_grupos_por_materia, 2) if avg_grupos_por_materia else 0
                }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de grupos: {e}")
            return {}

    def obtener_opciones_filtro(self) -> Dict[str, List[str]]:
        """Obtiene listas únicas de carreras y periodos académicos para los filtros de la UI."""
        try:
            with self.db_manager.cursor() as cursor:
                # Obtener carreras únicas y no nulas
                cursor.execute("SELECT DISTINCT carrera FROM GruposMateria WHERE carrera IS NOT NULL ORDER BY carrera")
                carreras = [row[0] for row in cursor.fetchall()]
                
                # Obtener periodos únicos y no nulos
                cursor.execute("SELECT DISTINCT periodo_academico FROM GruposMateria WHERE periodo_academico IS NOT NULL ORDER BY periodo_academico DESC")
                periodos = [row[0] for row in cursor.fetchall()]
                
                return {
                    "carreras": carreras,
                    "periodos": periodos
                }
        except Exception as e:
            logger.error(f"Error obteniendo opciones de filtro: {e}")
            return {"carreras": [], "periodos": []}
