"""
Repositorio para operaciones CRUD de materias
"""

import logging
from typing import List, Optional
from database.repositories.base_repository import BaseRepository
from database.models import Materia, MateriaCompleta

logger = logging.getLogger(__name__)

class MateriaRepository(BaseRepository):
    """Repositorio para gestionar materias en la base de datos"""
    
    def obtener_todas(self) -> List[Materia]:
        """Obtiene todas las materias"""
        query = "SELECT codigo_materia, nombre_materia, creditos FROM Materias ORDER BY nombre_materia"
        resultados = self._ejecutar_query(query)
        
        return [
            Materia(codigo_materia=row[0], nombre_materia=row[1], creditos=row[2])
            for row in resultados
        ]
    
    def obtener_por_codigo(self, codigo: str) -> Optional[Materia]:
        """Obtiene una materia por su código"""
        query = "SELECT codigo_materia, nombre_materia, creditos FROM Materias WHERE codigo_materia = ?"
        resultados = self._ejecutar_query(query, (codigo,))
        
        if not resultados:
            return None
        
        row = resultados[0]
        return Materia(codigo_materia=row[0], nombre_materia=row[1], creditos=row[2])
    
    def crear(self, materia: Materia) -> bool:
        """Crea una nueva materia"""
        try:
            comando = """
                INSERT INTO Materias (codigo_materia, nombre_materia, creditos)
                VALUES (?, ?, ?)
            """
            self._ejecutar_comando(comando, (materia.codigo_materia, materia.nombre_materia, materia.creditos))
            logger.info(f"Materia creada: {materia.codigo_materia} - {materia.nombre_materia}")
            return True
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"La materia {materia.codigo_materia} ya existe")
            else:
                logger.error(f"Error creando materia {materia.codigo_materia}: {e}")
            return False
    
    def actualizar(self, materia: Materia) -> bool:
        """Actualiza una materia existente"""
        try:
            comando = """
                UPDATE Materias 
                SET nombre_materia = ?, creditos = ? 
                WHERE codigo_materia = ?
            """
            filas_afectadas = self._ejecutar_comando(
                comando, 
                (materia.nombre_materia, materia.creditos, materia.codigo_materia)
            )
            
            if filas_afectadas > 0:
                logger.info(f"Materia actualizada: {materia.codigo_materia}")
                return True
            else:
                logger.warning(f"No se encontró la materia {materia.codigo_materia} para actualizar")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando materia {materia.codigo_materia}: {e}")
            return False
    
    def eliminar(self, codigo: str) -> bool:
        """Elimina una materia y todos sus grupos/sesiones asociados"""
        try:
            comando = "DELETE FROM Materias WHERE codigo_materia = ?"
            filas_afectadas = self._ejecutar_comando(comando, (codigo,))
            
            if filas_afectadas > 0:
                logger.info(f"Materia eliminada: {codigo} (incluye grupos y sesiones)")
                return True
            else:
                logger.warning(f"No se encontró la materia {codigo} para eliminar")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando materia {codigo}: {e}")
            return False
    
    def obtener_con_detalles(self, codigo: str) -> Optional[MateriaCompleta]:
        """Obtiene una materia con todos sus grupos y sesiones"""
        # Primero obtener la materia
        materia = self.obtener_por_codigo(codigo)
        if not materia:
            return None
        
        try:
            # Obtener grupos con sus sesiones
            query = """
                SELECT 
                    g.id_grupo_materia,
                    g.nombre_grupo,
                    g.cupos,
                    s.id_sesion,
                    s.tipo_sesion,
                    s.dia_semana,
                    s.hora_inicio,
                    s.hora_fin,
                    s.docente,
                    s.salon
                FROM GruposMateria g
                LEFT JOIN SesionesClase s ON g.id_grupo_materia = s.id_grupo_materia_fk
                WHERE g.codigo_materia_fk = ?
                ORDER BY g.nombre_grupo, s.dia_semana, s.hora_inicio
            """
            
            resultados = self._ejecutar_query(query, (codigo,))
            
            # Procesar resultados para construir la estructura
            from database.models import GrupoMateria, SesionClase, GrupoCompleto
            
            grupos_dict = {}
            
            for row in resultados:
                id_grupo = row[0]
                
                # Crear grupo si no existe
                if id_grupo not in grupos_dict:
                    grupo = GrupoMateria(
                        id_grupo_materia=id_grupo,
                        codigo_materia_fk=codigo,
                        nombre_grupo=row[1],
                        cupos=row[2]
                    )
                    grupos_dict[id_grupo] = GrupoCompleto(grupo=grupo, sesiones=[])
                
                # Agregar sesión si existe
                if row[3] is not None:  # id_sesion
                    sesion = SesionClase(
                        id_sesion=row[3],
                        id_grupo_materia_fk=id_grupo,
                        tipo_sesion=row[4],
                        dia_semana=row[5],
                        hora_inicio=row[6],
                        hora_fin=row[7],
                        docente=row[8],
                        salon=row[9]
                    )
                    grupos_dict[id_grupo].sesiones.append(sesion)
            
            return MateriaCompleta(materia=materia, grupos=list(grupos_dict.values()))
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de materia {codigo}: {e}")
            return None
    
    def obtener_horarios(self, codigo: str) -> List[dict]:
        """Obtiene todos los horarios de una materia en formato dict para compatibilidad"""
        query = """
            SELECT
                s.dia_semana,
                s.hora_inicio,
                s.hora_fin,
                g.nombre_grupo,
                s.docente,
                s.salon,
                s.tipo_sesion
            FROM GruposMateria g
            INNER JOIN SesionesClase s ON g.id_grupo_materia = s.id_grupo_materia_fk
            WHERE g.codigo_materia_fk = ?
            ORDER BY g.nombre_grupo, s.dia_semana, s.hora_inicio
        """
        
        resultados = self._ejecutar_query(query, (codigo,))
        
        columnas = ["dia_semana", "hora_inicio", "hora_fin", "nombre_grupo", "docente", "salon", "tipo_sesion"]
        return [dict(zip(columnas, row)) for row in resultados]
    
    def buscar(self, termino: str) -> List[Materia]:
        """Busca materias por nombre o código"""
        termino_lower = f"%{termino.lower()}%"
        query = """
            SELECT codigo_materia, nombre_materia, creditos 
            FROM Materias 
            WHERE LOWER(nombre_materia) LIKE ? OR LOWER(codigo_materia) LIKE ?
            ORDER BY nombre_materia
        """
        
        resultados = self._ejecutar_query(query, (termino_lower, termino_lower))
        return [
            Materia(codigo_materia=row[0], nombre_materia=row[1], creditos=row[2])
            for row in resultados
        ]
    
    def existe(self, codigo: str) -> bool:
        """Verifica si existe una materia con el código dado"""
        return self._existe_registro("Materias", "codigo_materia", codigo)
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas generales de las materias"""
        try:
            stats = {
                'total_materias': self._contar_registros("Materias"),
                'materias_con_grupos': 0,
                'materias_sin_grupos': 0,
                'total_creditos': 0,
                'promedio_creditos': 0
            }
            
            # Materias con y sin grupos
            query_con_grupos = """
                SELECT COUNT(DISTINCT m.codigo_materia) 
                FROM Materias m 
                INNER JOIN GruposMateria g ON m.codigo_materia = g.codigo_materia_fk
            """
            resultado = self._ejecutar_query(query_con_grupos)
            stats['materias_con_grupos'] = resultado[0][0] if resultado else 0
            stats['materias_sin_grupos'] = stats['total_materias'] - stats['materias_con_grupos']
            
            # Total y promedio de créditos
            query_creditos = "SELECT SUM(creditos), AVG(creditos) FROM Materias WHERE creditos IS NOT NULL"
            resultado = self._ejecutar_query(query_creditos)
            if resultado and resultado[0][0] is not None:
                stats['total_creditos'] = resultado[0][0]
                stats['promedio_creditos'] = round(resultado[0][1], 2) if resultado[0][1] else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de materias: {e}")
            return {'error': str(e)}

    def obtener_por_filtro(self, carrera: str, periodo: str) -> List[Materia]:
        """Obtiene materias distintas basadas en carrera y periodo académico de sus grupos."""
        query = """
            SELECT DISTINCT m.codigo_materia, m.nombre_materia, m.creditos
            FROM Materias m
            INNER JOIN GruposMateria gm ON m.codigo_materia = gm.codigo_materia_fk
            WHERE gm.carrera = ? AND gm.periodo_academico = ?
            ORDER BY m.nombre_materia
        """
        resultados = self._ejecutar_query(query, (carrera, periodo))
        return [
            Materia(codigo_materia=row[0], nombre_materia=row[1], creditos=row[2])
            for row in resultados
        ]
