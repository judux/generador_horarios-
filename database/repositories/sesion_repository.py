"""
Repositorio para operaciones CRUD de sesiones de clase
"""

import logging
from typing import List, Optional
from database.repositories.base_repository import BaseRepository
from database.models import SesionClase

logger = logging.getLogger(__name__)

class SesionRepository(BaseRepository):
    """Repositorio para gestionar sesiones de clase"""
    
    def obtener_por_grupo(self, id_grupo: int) -> List[SesionClase]:
        """Obtiene todas las sesiones de un grupo"""
        query = """
            SELECT id_sesion, id_grupo_materia_fk, tipo_sesion, dia_semana, 
                   hora_inicio, hora_fin, docente, salon
            FROM SesionesClase 
            WHERE id_grupo_materia_fk = ? 
            ORDER BY dia_semana, hora_inicio
        """
        resultados = self._ejecutar_query(query, (id_grupo,))
        
        return [
            SesionClase(
                id_sesion=row[0],
                id_grupo_materia_fk=row[1],
                tipo_sesion=row[2],
                dia_semana=row[3],
                hora_inicio=row[4],
                hora_fin=row[5],
                docente=row[6],
                salon=row[7]
            )
            for row in resultados
        ]
    
    def obtener_por_id(self, id_sesion: int) -> Optional[SesionClase]:
        """Obtiene una sesión por su ID"""
        query = """
            SELECT id_sesion, id_grupo_materia_fk, tipo_sesion, dia_semana, 
                   hora_inicio, hora_fin, docente, salon
            FROM SesionesClase 
            WHERE id_sesion = ?
        """
        resultados = self._ejecutar_query(query, (id_sesion,))
        
        if not resultados:
            return None
        
        row = resultados[0]
        return SesionClase(
            id_sesion=row[0],
            id_grupo_materia_fk=row[1],
            tipo_sesion=row[2],
            dia_semana=row[3],
            hora_inicio=row[4],
            hora_fin=row[5],
            docente=row[6],
            salon=row[7]
        )
    
    def crear(self, sesion: SesionClase) -> Optional[int]:
        """Crea una nueva sesión y retorna su ID"""
        try:
            # Verificar que el grupo existe
            if not self._existe_registro("GruposMateria", "id_grupo_materia", sesion.id_grupo_materia_fk):
                logger.error(f"No existe el grupo ID {sesion.id_grupo_materia_fk}")
                return None
            
            comando = """
                INSERT INTO SesionesClase 
                (id_grupo_materia_fk, tipo_sesion, dia_semana, hora_inicio, hora_fin, docente, salon)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            id_sesion = self._ejecutar_comando(
                comando,
                (
                    sesion.id_grupo_materia_fk,
                    sesion.tipo_sesion,
                    sesion.dia_semana,
                    sesion.hora_inicio,
                    sesion.hora_fin,
                    sesion.docente,
                    sesion.salon
                )
            )
            
            logger.info(f"Sesión creada: ID {id_sesion} para grupo {sesion.id_grupo_materia_fk}")
            return id_sesion
            
        except Exception as e:
            logger.error(f"Error creando sesión para grupo {sesion.id_grupo_materia_fk}: {e}")
            return None
    
    def actualizar(self, sesion: SesionClase) -> bool:
        """Actualiza una sesión existente"""
        try:
            comando = """
                UPDATE SesionesClase 
                SET tipo_sesion = ?, dia_semana = ?, hora_inicio = ?, 
                    hora_fin = ?, docente = ?, salon = ?
                WHERE id_sesion = ?
            """
            filas_afectadas = self._ejecutar_comando(
                comando,
                (
                    sesion.tipo_sesion,
                    sesion.dia_semana,
                    sesion.hora_inicio,
                    sesion.hora_fin,
                    sesion.docente,
                    sesion.salon,
                    sesion.id_sesion
                )
            )
            
            if filas_afectadas > 0:
                logger.info(f"Sesión actualizada: ID {sesion.id_sesion}")
                return True
            else:
                logger.warning(f"No se encontró la sesión ID {sesion.id_sesion} para actualizar")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando sesión ID {sesion.id_sesion}: {e}")
            return False
    
    def eliminar(self, id_sesion: int) -> bool:
        """Elimina una sesión específica"""
        try:
            comando = "DELETE FROM SesionesClase WHERE id_sesion = ?"
            filas_afectadas = self._ejecutar_comando(comando, (id_sesion,))
            
            if filas_afectadas > 0:
                logger.info(f"Sesión eliminada: ID {id_sesion}")
                return True
            else:
                logger.warning(f"No se encontró la sesión ID {id_sesion} para eliminar")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando sesión ID {id_sesion}: {e}")
            return False
    
    def obtener_por_horario(self, dia: str, hora_inicio: str, hora_fin: str) -> List[SesionClase]:
        """Obtiene sesiones que coinciden con un horario específico"""
        query = """
            SELECT id_sesion, id_grupo_materia_fk, tipo_sesion, dia_semana, 
                   hora_inicio, hora_fin, docente, salon
            FROM SesionesClase 
            WHERE dia_semana = ? AND (
                (hora_inicio <= ? AND hora_fin > ?) OR
                (hora_inicio < ? AND hora_fin >= ?) OR
                (hora_inicio >= ? AND hora_fin <= ?)
            )
            ORDER BY hora_inicio
        """
        resultados = self._ejecutar_query(query, (dia, hora_inicio, hora_inicio, hora_fin, hora_fin, hora_inicio, hora_fin))
        
        return [
            SesionClase(
                id_sesion=row[0],
                id_grupo_materia_fk=row[1],
                tipo_sesion=row[2],
                dia_semana=row[3],
                hora_inicio=row[4],
                hora_fin=row[5],
                docente=row[6],
                salon=row[7]
            )
            for row in resultados
        ]
    
    def obtener_por_docente(self, docente: str) -> List[SesionClase]:
        """Obtiene todas las sesiones de un docente"""
        query = """
            SELECT id_sesion, id_grupo_materia_fk, tipo_sesion, dia_semana, 
                   hora_inicio, hora_fin, docente, salon
            FROM SesionesClase 
            WHERE docente = ?
            ORDER BY dia_semana, hora_inicio
        """
        resultados = self._ejecutar_query(query, (docente,))
        
        return [
            SesionClase(
                id_sesion=row[0],
                id_grupo_materia_fk=row[1],
                tipo_sesion=row[2],
                dia_semana=row[3],
                hora_inicio=row[4],
                hora_fin=row[5],
                docente=row[6],
                salon=row[7]
            )
            for row in resultados
        ]
    
    def obtener_por_salon(self, salon: str) -> List[SesionClase]:
        """Obtiene todas las sesiones que usan un salón específico"""
        query = """
            SELECT id_sesion, id_grupo_materia_fk, tipo_sesion, dia_semana, 
                   hora_inicio, hora_fin, docente, salon
            FROM SesionesClase 
            WHERE salon = ?
            ORDER BY dia_semana, hora_inicio
        """
        resultados = self._ejecutar_query(query, (salon,))
        
        return [
            SesionClase(
                id_sesion=row[0],
                id_grupo_materia_fk=row[1],
                tipo_sesion=row[2],
                dia_semana=row[3],
                hora_inicio=row[4],
                hora_fin=row[5],
                docente=row[6],
                salon=row[7]
            )
            for row in resultados
        ]
    
    def existe(self, id_sesion: int) -> bool:
        """Verifica si existe una sesión con el ID dado"""
        return self._existe_registro("SesionesClase", "id_sesion", id_sesion)
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas de las sesiones"""
        try:
            stats = {
                'total_sesiones': self._contar_registros("SesionesClase"),
                'sesiones_por_tipo': {},
                'sesiones_por_dia': {},
                'docentes_unicos': 0,
                'salones_unicos': 0
            }
            
            # Sesiones por tipo
            query_tipos = "SELECT tipo_sesion, COUNT(*) FROM SesionesClase GROUP BY tipo_sesion"
            resultados = self._ejecutar_query(query_tipos)
            stats['sesiones_por_tipo'] = {row[0]: row[1] for row in resultados}
            
            # Sesiones por día
            query_dias = "SELECT dia_semana, COUNT(*) FROM SesionesClase GROUP BY dia_semana"
            resultados = self._ejecutar_query(query_dias)
            stats['sesiones_por_dia'] = {row[0]: row[1] for row in resultados}
            
            # Docentes únicos
            query_docentes = "SELECT COUNT(DISTINCT docente) FROM SesionesClase WHERE docente IS NOT NULL"
            resultado = self._ejecutar_query(query_docentes)
            stats['docentes_unicos'] = resultado[0][0] if resultado else 0
            
            # Salones únicos
            query_salones = "SELECT COUNT(DISTINCT salon) FROM SesionesClase WHERE salon IS NOT NULL"
            resultado = self._ejecutar_query(query_salones)
            stats['salones_unicos'] = resultado[0][0] if resultado else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de sesiones: {e}")
            return {'error': str(e)}
