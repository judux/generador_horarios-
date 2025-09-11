"""
Servicio de lógica de negocio para materias
"""

import logging
from typing import Dict, List, Optional, Any
from database.connection import DatabaseManager
from database.repositories.materia_repository import MateriaRepository
from database.repositories.grupo_repository import GrupoRepository
from database.repositories.sesion_repository import SesionRepository
from database.models import Materia, GrupoMateria, SesionClase
from logica.services.validacion_service import ValidacionService

logger = logging.getLogger(__name__)

class MateriaService:
    """Servicio para la lógica de negocio de materias"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.materia_repo = MateriaRepository(db_manager)
        self.grupo_repo = GrupoRepository(db_manager)
        self.sesion_repo = SesionRepository(db_manager)
        self.validacion_service = ValidacionService()
    
    def obtener_todas_las_materias(self) -> List[Dict[str, Any]]:
        """Obtiene todas las materias con sus grupos y sesiones organizadas"""
        try:
            materias = self.materia_repo.obtener_todas()
            resultado = []
            
            for materia in materias:
                materia_dict = {
                    'codigo': materia.codigo_materia,
                    'nombre': materia.nombre_materia,
                    'creditos': materia.creditos or 0,
                    'grupos': {}
                }
                
                # Obtener grupos de la materia
                grupos = self.grupo_repo.obtener_por_materia(materia.codigo_materia)
                
                for grupo in grupos:
                    # Obtener sesiones del grupo
                    sesiones = self.sesion_repo.obtener_por_grupo(grupo.id_grupo_materia)
                    
                    # Organizar sesiones por día
                    sesiones_organizadas = []
                    docente = None
                    
                    for sesion in sesiones:
                        sesiones_organizadas.append({
                            'dia_semana': sesion.dia_semana,
                            'hora_inicio': sesion.hora_inicio,
                            'hora_fin': sesion.hora_fin,
                            'tipo_sesion': sesion.tipo_sesion,
                            'salon': sesion.salon or 'N/A'
                        })
                        
                        if not docente and sesion.docente:
                            docente = sesion.docente
                    
                    materia_dict['grupos'][grupo.nombre_grupo] = {
                        'sesiones': sesiones_organizadas,
                        'docente': docente or 'N/A',
                        'cupos': grupo.cupos
                    }
                
                resultado.append(materia_dict)
            
            logger.info(f"Obtenidas {len(resultado)} materias con sus detalles")
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo todas las materias: {e}")
            return []
    
    def buscar_materias(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Busca materias por término de búsqueda"""
        try:
            if not termino_busqueda or len(termino_busqueda.strip()) < 2:
                return []
            
            materias_encontradas = self.materia_repo.buscar(termino_busqueda.strip())
            
            resultado = []
            for materia in materias_encontradas:
                resultado.append({
                    'codigo': materia.codigo_materia,
                    'nombre': materia.nombre_materia,
                    'creditos': materia.creditos or 0
                })
            
            logger.info(f"Encontradas {len(resultado)} materias para el término: {termino_busqueda}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error buscando materias: {e}")
            return []
    
    def obtener_detalle_materia(self, codigo_materia: str) -> Optional[Dict[str, Any]]:
        """Obtiene el detalle completo de una materia específica"""
        try:
            materia_completa = self.materia_repo.obtener_con_detalles(codigo_materia)
            
            if not materia_completa:
                return None
            
            resultado = {
                'codigo': materia_completa.materia.codigo_materia,
                'nombre': materia_completa.materia.nombre_materia,
                'creditos': materia_completa.materia.creditos or 0,
                'grupos': []
            }
            
            for grupo_completo in materia_completa.grupos:
                grupo_dict = {
                    'id': grupo_completo.grupo.id_grupo_materia,
                    'nombre': grupo_completo.grupo.nombre_grupo,
                    'cupos': grupo_completo.grupo.cupos,
                    'sesiones': []
                }
                
                docente = None
                for sesion in grupo_completo.sesiones:
                    grupo_dict['sesiones'].append({
                        'id': sesion.id_sesion,
                        'tipo': sesion.tipo_sesion,
                        'dia': sesion.dia_semana,
                        'hora_inicio': sesion.hora_inicio,
                        'hora_fin': sesion.hora_fin,
                        'salon': sesion.salon or 'N/A'
                    })
                    
                    if not docente and sesion.docente:
                        docente = sesion.docente
                
                grupo_dict['docente'] = docente or 'N/A'
                resultado['grupos'].append(grupo_dict)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error obteniendo detalle de materia {codigo_materia}: {e}")
            return None
    
    def crear_materia(self, codigo: str, nombre: str, creditos: Optional[int] = None) -> Dict[str, Any]:
        """Crea una nueva materia con validación"""
        try:
            # Validar datos de entrada
            validacion_codigo = self.validacion_service.validar_codigo_materia(codigo)
            if not validacion_codigo['es_valido']:
                return {
                    'exito': False,
                    'mensaje': validacion_codigo['mensaje'],
                    'sugerencias': validacion_codigo.get('sugerencias', [])
                }
            
            validacion_nombre = self.validacion_service.validar_nombre_materia(nombre)
            if not validacion_nombre['es_valido']:
                return {
                    'exito': False,
                    'mensaje': validacion_nombre['mensaje'],
                    'sugerencias': validacion_nombre.get('sugerencias', [])
                }
            
            validacion_creditos = self.validacion_service.validar_creditos(creditos)
            if not validacion_creditos['es_valido']:
                return {
                    'exito': False,
                    'mensaje': validacion_creditos['mensaje'],
                    'sugerencias': validacion_creditos.get('sugerencias', [])
                }
            
            # Crear modelo de materia
            materia = Materia(
                codigo_materia=validacion_codigo.get('codigo_normalizado', codigo.upper()),
                nombre_materia=validacion_nombre.get('nombre_normalizado', nombre.upper()),
                creditos=validacion_creditos.get('creditos_validados', creditos)
            )
            
            # Intentar crear en la base de datos
            if self.materia_repo.crear(materia):
                return {
                    'exito': True,
                    'mensaje': f'Materia {materia.codigo_materia} creada exitosamente',
                    'materia_creada': {
                        'codigo': materia.codigo_materia,
                        'nombre': materia.nombre_materia,
                        'creditos': materia.creditos
                    }
                }
            else:
                return {
                    'exito': False,
                    'mensaje': 'No se pudo crear la materia (posible código duplicado)'
                }
                
        except Exception as e:
            logger.error(f"Error creando materia: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}'
            }
    
    def actualizar_materia(self, codigo: str, nuevo_nombre: Optional[str] = None, 
                          nuevos_creditos: Optional[int] = None) -> Dict[str, Any]:
        """Actualiza una materia existente"""
        try:
            # Verificar que la materia existe
            if not self.materia_repo.existe(codigo):
                return {
                    'exito': False,
                    'mensaje': f'No existe la materia con código {codigo}'
                }
            
            # Obtener materia actual
            materia_actual = self.materia_repo.obtener_por_codigo(codigo)
            if not materia_actual:
                return {
                    'exito': False,
                    'mensaje': 'Error obteniendo datos de la materia'
                }
            
            # Validar nuevos datos si se proporcionan
            nombre_final = materia_actual.nombre_materia
            creditos_final = materia_actual.creditos
            
            if nuevo_nombre:
                validacion_nombre = self.validacion_service.validar_nombre_materia(nuevo_nombre)
                if not validacion_nombre['es_valido']:
                    return {
                        'exito': False,
                        'mensaje': f'Nombre inválido: {validacion_nombre["mensaje"]}'
                    }
                nombre_final = validacion_nombre.get('nombre_normalizado', nuevo_nombre.upper())
            
            if nuevos_creditos is not None:
                validacion_creditos = self.validacion_service.validar_creditos(nuevos_creditos)
                if not validacion_creditos['es_valido']:
                    return {
                        'exito': False,
                        'mensaje': f'Créditos inválidos: {validacion_creditos["mensaje"]}'
                    }
                creditos_final = validacion_creditos.get('creditos_validados', nuevos_creditos)
            
            # Crear materia actualizada
            materia_actualizada = Materia(
                codigo_materia=codigo,
                nombre_materia=nombre_final,
                creditos=creditos_final
            )
            
            # Actualizar en base de datos
            if self.materia_repo.actualizar(materia_actualizada):
                return {
                    'exito': True,
                    'mensaje': f'Materia {codigo} actualizada exitosamente',
                    'materia_actualizada': {
                        'codigo': materia_actualizada.codigo_materia,
                        'nombre': materia_actualizada.nombre_materia,
                        'creditos': materia_actualizada.creditos
                    }
                }
            else:
                return {
                    'exito': False,
                    'mensaje': 'No se pudo actualizar la materia'
                }
                
        except Exception as e:
            logger.error(f"Error actualizando materia {codigo}: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}'
            }
    
    def eliminar_materia(self, codigo: str) -> Dict[str, Any]:
        """Elimina una materia y todos sus datos asociados"""
        try:
            # Verificar que la materia existe
            if not self.materia_repo.existe(codigo):
                return {
                    'exito': False,
                    'mensaje': f'No existe la materia con código {codigo}'
                }
            
            # Obtener información antes de eliminar
            materia = self.materia_repo.obtener_por_codigo(codigo)
            grupos = self.grupo_repo.obtener_por_materia(codigo)
            
            total_sesiones = 0
            for grupo in grupos:
                sesiones = self.sesion_repo.obtener_por_grupo(grupo.id_grupo_materia)
                total_sesiones += len(sesiones)
            
            # Eliminar (cascada automática eliminará grupos y sesiones)
            if self.materia_repo.eliminar(codigo):
                return {
                    'exito': True,
                    'mensaje': f'Materia {codigo} eliminada exitosamente',
                    'detalles_eliminacion': {
                        'materia': materia.nombre_materia if materia else 'N/A',
                        'grupos_eliminados': len(grupos),
                        'sesiones_eliminadas': total_sesiones
                    }
                }
            else:
                return {
                    'exito': False,
                    'mensaje': 'No se pudo eliminar la materia'
                }
                
        except Exception as e:
            logger.error(f"Error eliminando materia {codigo}: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}'
            }
    
    def obtener_estadisticas_materias(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de las materias"""
        try:
            stats_materias = self.materia_repo.obtener_estadisticas()
            stats_grupos = self.grupo_repo.obtener_estadisticas()
            stats_sesiones = self.sesion_repo.obtener_estadisticas()
            
            return {
                'materias': stats_materias,
                'grupos': stats_grupos,
                'sesiones': stats_sesiones,
                'resumen': {
                    'total_materias': stats_materias.get('total_materias', 0),
                    'total_grupos': stats_grupos.get('total_grupos', 0),
                    'total_sesiones': stats_sesiones.get('total_sesiones', 0),
                    'promedio_grupos_por_materia': round(
                        stats_grupos.get('total_grupos', 0) / max(stats_materias.get('total_materias', 1), 1), 2
                    ),
                    'promedio_sesiones_por_grupo': round(
                        stats_sesiones.get('total_sesiones', 0) / max(stats_grupos.get('total_grupos', 1), 1), 2
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de materias: {e}")
            return {'error': str(e)}
