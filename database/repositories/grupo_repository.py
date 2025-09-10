"""
Repositorio para operaciones CRUD de grupos de materia
"""

import logging
from typing import List, Optional
from database.repositories.base_repository import BaseRepository
from database.models import GrupoMateria

logger = logging.getLogger(__name__)

class GrupoRepository(BaseRepository):
    """Repositorio para gestionar grupos de materia"""
    
    def obtener_por_materia(self, codigo_materia: str) -> List[GrupoMateria]:
        """Obtiene todos los grupos de una materia"""
        query = """
            SELECT id_grupo_materia, codigo_materia_fk, nombre_grupo, cupos 
            FROM GruposMateria 
            WHERE codigo_materia_fk = ? 
            ORDER BY nombre_grupo
        """
        resultados = self._ejecutar_query(query, (codigo_materia,))
        
        return [
            GrupoMateria(
                id_grupo_materia=row[0],
                codigo_materia_fk=row[1],
                nombre_grupo=row[2],
                cupos=row[3]
            )
            for row in resultados
        ]
    
    def obtener_por_id(self, id_grupo: int) -> Optional[GrupoMateria]:
        """Obtiene un grupo por su ID"""
        query = """
            SELECT id_grupo_materia, codigo_materia_fk, nombre_grupo, cupos 
            FROM GruposMateria 
            WHERE id_grupo_materia = ?
        """
        resultados = self._ejecutar_query(query, (id_grupo,))
        
        if not resultados:
            return None
        
        row = resultados[0]
        return GrupoMateria(
            id_grupo_materia=row[0],
            codigo_materia_fk=row[1],
            nombre_grupo=row[2],
            cupos=row[3]
        )
    
    def crear(self, grupo: GrupoMateria) -> Optional[int]:
        """Crea un nuevo grupo y retorna su ID"""
        try:
            # Verificar que la materia existe
            if not self._existe_registro("Materias", "codigo_materia", grupo.codigo_materia_fk):
                logger.error(f"No existe la materia {grupo.codigo_materia_fk}")
                return None
            
            comando = """
                INSERT INTO GruposMateria (codigo_materia_fk, nombre_grupo, cupos)
                VALUES (?, ?, ?)
            """
            id_grupo = self._ejecutar_comando(
                comando, 
                (grupo.codigo_materia_fk, grupo.nombre_grupo, grupo.cupos)
            )
            
            logger.info(f"Grupo creado: ID {id_grupo} para {grupo.codigo_materia_fk} (Grupo {grupo.nombre_grupo})")
            return id_grupo
            
        except Exception as e:
            logger.error(f"Error creando grupo para {grupo.codigo_materia_fk}: {e}")
            return None
    
    def actualizar(self, grupo: GrupoMateria) -> bool:
        """Actualiza un grupo existente"""
        try:
            comando = """
                UPDATE GruposMateria 
                SET nombre_grupo = ?, cupos = ? 
                WHERE id_grupo_materia = ?
            """
            filas_afectadas = self._ejecutar_comando(
                comando, 
                (grupo.nombre_grupo, grupo.cupos, grupo.id_grupo_materia)
            )
            
            if filas_afectadas > 0:
                logger.info(f"Grupo actualizado: ID {grupo.id_grupo_materia}")
                return True
            else:
                logger.warning(f"No se encontró el grupo ID {grupo.id_grupo_materia} para actualizar")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando grupo ID {grupo.id_grupo_materia}: {e}")
            return False
    
    def eliminar(self, id_grupo: int) -> bool:
        """Elimina un grupo y todas sus sesiones asociadas"""
        try:
            comando = "DELETE FROM GruposMateria WHERE id_grupo_materia = ?"
            filas_afectadas = self._ejecutar_comando(comando, (id_grupo,))
            
            if filas_afectadas > 0:
                logger.info(f"Grupo eliminado: ID {id_grupo} (incluye sesiones)")
                return True
            else:
                logger.warning(f"No se encontró el grupo ID {id_grupo} para eliminar")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando grupo ID {id_grupo}: {e}")
            return False
    
    def obtener_todos(self) -> List[GrupoMateria]:
        """Obtiene todos los grupos del sistema"""
        query = """
            SELECT id_grupo_materia, codigo_materia_fk, nombre_grupo, cupos 
            FROM GruposMateria 
            ORDER BY codigo_materia_fk, nombre_grupo
        """
        resultados = self._ejecutar_query(query)
        
        return [
            GrupoMateria(
                id_grupo_materia=row[0],
                codigo_materia_fk=row[1],
                nombre_grupo=row[2],
                cupos=row[3]
            )
            for row in resultados
        ]
    
    def existe(self, id_grupo: int) -> bool:
        """Verifica si existe un grupo con el ID dado"""
        return self._existe_registro("GruposMateria", "id_grupo_materia", id_grupo)
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas de los grupos"""
        try:
            stats = {
                'total_grupos': self._contar_registros("GruposMateria"),
                'grupos_con_sesiones': 0,
                'grupos_sin_sesiones': 0,
                'total_cupos': 0
            }
            
            # Grupos con y sin sesiones
            query_con_sesiones = """
                SELECT COUNT(DISTINCT g.id_grupo_materia) 
                FROM GruposMateria g 
                INNER JOIN SesionesClase s ON g.id_grupo_materia = s.id_grupo_materia_fk
            """
            resultado = self._ejecutar_query(query_con_sesiones)
            stats['grupos_con_sesiones'] = resultado[0][0] if resultado else 0
            stats['grupos_sin_sesiones'] = stats['total_grupos'] - stats['grupos_con_sesiones']
            
            # Total de cupos
            query_cupos = "SELECT SUM(cupos) FROM GruposMateria WHERE cupos IS NOT NULL"
            resultado = self._ejecutar_query(query_cupos)
            stats['total_cupos'] = resultado[0][0] if resultado and resultado[0][0] else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de grupos: {e}")
            return {'error': str(e)}
