"""
Servicio de lógica de negocio para manejo de horarios
"""
from __future__ import annotations
import logging
from typing import Dict, List, Tuple, Optional, Callable, Any
from datetime import datetime, timedelta
from database.connection import DatabaseManager
from database.repositories.materia_repository import MateriaRepository
from database.repositories.grupo_repository import GrupoRepository
from database.repositories.sesion_repository import SesionRepository
from database.models import HorarioAsignado, Materia, GrupoMateria, SesionClase
from logica.services.validacion_service import ValidacionService

logger = logging.getLogger(__name__)

class Command:
    """Clase base para el patrón Command."""
    def __init__(self, service: 'HorarioService'):
        self.service = service

    def execute(self) -> Dict[str, Any]:
        raise NotImplementedError

    def undo(self) -> Dict[str, Any]:
        raise NotImplementedError

class HorarioService:
    """Servicio para la lógica de negocio de horarios"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.materia_repo = MateriaRepository(db_manager)
        self.grupo_repo = GrupoRepository(db_manager)
        self.sesion_repo = SesionRepository(db_manager)
        self.validacion_service = ValidacionService()
        
        # Estado del horario actual
        self.horario_asignado: Dict[Tuple[str, str], HorarioAsignado] = {}
        self.total_creditos = 0
        self.materias_agregadas: Dict[str, int] = {} # Para contar créditos por materia
    
    def obtener_horario_actual(self) -> Dict[Tuple[str, str], HorarioAsignado]:
        """Obtiene el horario actualmente asignado"""
        return self.horario_asignado.copy()
    
    def obtener_total_creditos(self) -> int:
        """Obtiene el total de créditos del horario actual"""
        return self.total_creditos

    def crear_comando_agregar_grupo(self, codigo_materia: str, nombre_grupo: str) -> Command:
        """Crea un comando para agregar un grupo al horario."""
        return AgregarGrupoCommand(self, codigo_materia, nombre_grupo)

    def crear_comando_eliminar_grupo(self, dia: str, hora: str) -> Optional[Command]:
        """Crea un comando para eliminar un grupo del horario."""
        clave_horario = (dia, hora)
        if clave_horario not in self.horario_asignado:
            return None
        
        asignacion = self.horario_asignado[clave_horario]
        codigo_materia = asignacion.materia.codigo_materia
        nombre_grupo = asignacion.grupo.nombre_grupo
        
        return EliminarGrupoCommand(self, codigo_materia, nombre_grupo)

    def _internal_agregar_grupo(self, codigo_materia: str, nombre_grupo: str) -> Dict[str, Any]:
        """Lógica interna para agregar un grupo. Usado por el comando."""
        materia = self.materia_repo.obtener_por_codigo(codigo_materia)
        grupo = self.grupo_repo.obtener_por_materia_y_nombre(codigo_materia, nombre_grupo)
        sesiones = self.sesion_repo.obtener_por_grupo(grupo.id_grupo_materia)

        # Agregar las sesiones al horario
        self._agregar_sesiones_al_horario(materia, grupo, sesiones)
        
        creditos_materia = materia.creditos or 0
        if codigo_materia not in self.materias_agregadas:
            self.total_creditos += creditos_materia
            self.materias_agregadas[codigo_materia] = 1
        else:
            self.materias_agregadas[codigo_materia] += 1

        return {
            'exito': True,
            'mensaje': f"'{nombre_grupo}' de {materia.nombre_materia} agregado.",
            'codigo_materia': codigo_materia,
            'nombre_grupo': nombre_grupo
        }

    def _internal_eliminar_grupo(self, codigo_materia: str, nombre_grupo: str) -> Dict[str, Any]:
        """Lógica interna para eliminar un grupo. Usado por el comando."""
        claves_a_eliminar = []
        materia_info = None
        for clave, asig in self.horario_asignado.items():
            if (asig.materia.codigo_materia == codigo_materia and 
                asig.grupo.nombre_grupo == nombre_grupo):
                claves_a_eliminar.append(clave)
                if not materia_info:
                    materia_info = asig.materia

        for clave in claves_a_eliminar:
            del self.horario_asignado[clave]

        if materia_info:
            self.materias_agregadas[codigo_materia] -= 1
            if self.materias_agregadas[codigo_materia] == 0:
                self.total_creditos -= (materia_info.creditos or 0)
                del self.materias_agregadas[codigo_materia]

        return {
            'exito': True,
            'mensaje': f"Grupo '{nombre_grupo}' de {materia_info.nombre_materia} eliminado.",
            'codigo_materia': codigo_materia,
            'nombre_grupo': nombre_grupo
        }

    def _verificar_conflictos_horario(self, sesiones: List[SesionClase]) -> List[Dict[str, str]]:
        """Verifica si hay conflictos de horario con las sesiones a agregar"""
        conflictos = []
        
        for sesion in sesiones:
            # Generar todas las horas que ocupa la sesión
            horas_sesion = self._generar_horas_sesion(sesion)
            
            for dia, hora in horas_sesion:
                clave = (dia, hora)
                if clave in self.horario_asignado:
                    asignacion_existente = self.horario_asignado[clave]
                    conflictos.append({
                        'dia': dia,
                        'hora': hora,
                        'materia_existente': asignacion_existente.materia.nombre_materia
                    })
        
        return conflictos

    def _generar_horas_sesion(self, sesion: SesionClase) -> List[Tuple[str, str]]:
        """Genera lista de tuplas (dia, hora) que ocupa una sesión"""
        horas = []
        
        try:
            hora_inicio_dt = datetime.strptime(sesion.hora_inicio, "%H:%M")
            hora_fin_dt = datetime.strptime(sesion.hora_fin, "%H:%M")
            
            hora_actual = hora_inicio_dt
            while hora_actual < hora_fin_dt:
                hora_str = hora_actual.strftime("%H:%M")
                horas.append((sesion.dia_semana, hora_str))
                hora_actual += timedelta(hours=1)
                
        except ValueError as e:
            logger.error(f"Error procesando horas de sesión {sesion.id_sesion}: {e}")
        
        return horas

    def _agregar_sesiones_al_horario(self, materia: Materia, grupo: GrupoMateria, sesiones: List[SesionClase]):
        """Agrega las sesiones de un grupo al horario"""
        for sesion in sesiones:
            horas_sesion = self._generar_horas_sesion(sesion)
            
            for dia, hora in horas_sesion:
                horario_asignado = HorarioAsignado(
                    materia=materia,
                    grupo=grupo,
                    sesion=sesion,
                    dia=dia,
                    hora=hora
                )
                
                self.horario_asignado[(dia, hora)] = horario_asignado

    def agregar_grupo_al_horario(self, codigo_materia: str, nombre_grupo: str) -> Dict[str, any]:
        """
        Agrega un grupo de materia al horario
        Retorna un diccionario con el resultado de la operación
        """
        try:
            # Obtener información de la materia
            materia = self.materia_repo.obtener_por_codigo(codigo_materia)
            if not materia:
                return {
                    'exito': False,
                    'mensaje': f'No se encontró la materia {codigo_materia}',
                    'tipo': 'error'
                }
            
            # Obtener grupos de la materia
            grupos = self.grupo_repo.obtener_por_materia(codigo_materia)
            grupo_encontrado = None
            
            for grupo in grupos:
                if grupo.nombre_grupo == nombre_grupo:
                    grupo_encontrado = grupo
                    break
            
            if not grupo_encontrado:
                return {
                    'exito': False,
                    'mensaje': f'No se encontró el grupo {nombre_grupo} para la materia {codigo_materia}',
                    'tipo': 'error'
                }
            
            # Obtener sesiones del grupo
            sesiones = self.sesion_repo.obtener_por_grupo(grupo_encontrado.id_grupo_materia)
            
            if not sesiones:
                return {
                    'exito': False,
                    'mensaje': f'El grupo {nombre_grupo} no tiene sesiones programadas',
                    'tipo': 'warning'
                }
            
            # Verificar conflictos de horario
            conflictos = self._verificar_conflictos_horario(sesiones)
            
            if conflictos:
                mensaje_conflicto = "Conflictos de horario detectados:\n\n"
                for conflicto in conflictos:
                    mensaje_conflicto += f"• {conflicto['dia']} a las {conflicto['hora']} - {conflicto['materia_existente']}\n"
                
                return {
                    'exito': False,
                    'mensaje': mensaje_conflicto,
                    'tipo': 'conflict',
                    'conflictos': conflictos
                }
            
            # Agregar al horario
            self._agregar_sesiones_al_horario(materia, grupo_encontrado, sesiones)
            self._actualizar_creditos_agregar(materia)
            
            logger.info(f"Grupo agregado al horario: {nombre_grupo} de {materia.nombre_materia}")
            
            return {
                'exito': True,
                'mensaje': f"'{nombre_grupo}' de {materia.nombre_materia} agregado al horario",
                'tipo': 'success',
                'creditos_agregados': materia.creditos or 0,
                'total_creditos': self.total_creditos
            }
            
        except Exception as e:
            logger.error(f"Error agregando grupo al horario: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}',
                'tipo': 'error'
            }

    def _actualizar_creditos_agregar(self, materia: Materia):
        """Actualiza los créditos al agregar un grupo, evitando doble conteo."""
        codigo = materia.codigo_materia
        if codigo not in self.materias_agregadas:
            self.total_creditos += materia.creditos or 0
            self.materias_agregadas[codigo] = 0
        self.materias_agregadas[codigo] += 1
    
    def eliminar_del_horario(self, dia: str, hora: str) -> Dict[str, any]:
        """
        Elimina una materia específica del horario
        """
        try:
            clave_horario = (dia, hora)
            
            if clave_horario not in self.horario_asignado:
                return {
                    'exito': False,
                    'mensaje': 'No hay ninguna materia asignada en ese horario',
                    'tipo': 'warning'
                }
            
            # Obtener información de la asignación a eliminar
            asignacion = self.horario_asignado[clave_horario]
            codigo_materia = asignacion.materia.codigo_materia
            nombre_grupo = asignacion.grupo.nombre_grupo
            
            # Encontrar y eliminar todas las horas de este grupo específico
            claves_a_eliminar = []
            for clave, asig in self.horario_asignado.items():
                if (asig.materia.codigo_materia == codigo_materia and 
                    asig.grupo.nombre_grupo == nombre_grupo):
                    claves_a_eliminar.append(clave)
            
            # Eliminar las claves encontradas
            for clave in claves_a_eliminar:
                del self.horario_asignado[clave]
            
            # Actualizar créditos
            self._actualizar_creditos_eliminar(asignacion.materia)
            
            logger.info(f"Grupo eliminado del horario: {nombre_grupo} de {asignacion.materia.nombre_materia}")
            
            return {
                'exito': True,
                'mensaje': f'Grupo {nombre_grupo} eliminado del horario',
                'tipo': 'success',
                'creditos_eliminados': asignacion.materia.creditos or 0,
                'total_creditos': self.total_creditos
            }
            
        except Exception as e:
            logger.error(f"Error eliminando del horario: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}',
                'tipo': 'error'
            }

    def _actualizar_creditos_eliminar(self, materia: Materia):
        """Actualiza los créditos al eliminar un grupo."""
        codigo = materia.codigo_materia
        if codigo in self.materias_agregadas:
            self.materias_agregadas[codigo] -= 1
            if self.materias_agregadas[codigo] == 0:
                self.total_creditos -= materia.creditos or 0
                del self.materias_agregadas[codigo]
    
    def limpiar_horario(self) -> Dict[str, any]:
        """Limpia completamente el horario"""
        try:
            num_materias_eliminadas = len(set(
                asig.materia.codigo_materia for asig in self.horario_asignado.values()
            ))
            
            self.horario_asignado.clear()
            self.total_creditos = 0
            self.materias_agregadas.clear()
            
            logger.info("Horario limpiado completamente")
            
            return {
                'exito': True,
                'mensaje': f'Horario limpiado. Se eliminaron {num_materias_eliminadas} materias',
                'tipo': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error limpiando horario: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}',
                'tipo': 'error'
            }
    
    def obtener_estadisticas_horario(self) -> Dict[str, any]:
        """Obtiene estadísticas del horario actual"""
        try:
            materias_unicas = set(asig.materia.codigo_materia for asig in self.horario_asignado.values())
            
            # Contar sesiones por día
            sesiones_por_dia = {}
            for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
                sesiones_por_dia[dia] = len([
                    asig for asig in self.horario_asignado.values() 
                    if asig.dia == dia
                ])
            
            # Contar por tipo de sesión
            tipos_sesion = {}
            for asig in self.horario_asignado.values():
                tipo = asig.sesion.tipo_sesion
                tipos_sesion[tipo] = tipos_sesion.get(tipo, 0) + 1
            
            return {
                'total_materias': len(materias_unicas),
                'total_creditos': self.total_creditos,
                'total_sesiones': len(self.horario_asignado),
                'sesiones_por_dia': sesiones_por_dia,
                'tipos_sesion': tipos_sesion,
                'promedio_creditos_por_materia': round(self.total_creditos / len(materias_unicas), 2) if materias_unicas else 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del horario: {e}")
            return {'error': str(e)}
    
    def validar_carga_creditos(self) -> Dict[str, any]:
        """Valida la carga de créditos según estándares académicos"""
        resultado = {
            'es_valida': True,
            'nivel': 'normal',
            'mensaje': '',
            'recomendaciones': []
        }
        
        if self.total_creditos < 12:
            resultado['nivel'] = 'bajo'
            resultado['mensaje'] = 'Carga académica baja'
            resultado['recomendaciones'].append('Consider agregar más materias para cumplir con la carga mínima')
        elif self.total_creditos <= 18:
            resultado['nivel'] = 'normal'
            resultado['mensaje'] = 'Carga académica normal'
        elif self.total_creditos <= 22:
            resultado['nivel'] = 'alto'
            resultado['mensaje'] = 'Carga académica alta'
            resultado['recomendaciones'].append('Considere si puede manejar esta carga de trabajo')
        else:
            resultado['es_valida'] = False
            resultado['nivel'] = 'excesivo'
            resultado['mensaje'] = 'Carga académica excesiva'
            resultado['recomendaciones'].append('Se recomienda reducir la cantidad de créditos')
        
        return resultado
    
    def exportar_horario_json(self) -> Dict[str, any]:
        """Exporta el horario actual a formato JSON"""
        try:
            horario_export = {
                'metadata': {
                    'fecha_exportacion': datetime.now().isoformat(),
                    'total_materias': len(set(asig.materia.codigo_materia for asig in self.horario_asignado.values())),
                    'total_creditos': self.total_creditos
                },
                'horario': []
            }
            
            # Agrupar por materia y grupo
            materias_grupos = {}
            for asig in self.horario_asignado.values():
                clave = (asig.materia.codigo_materia, asig.grupo.nombre_grupo)
                if clave not in materias_grupos:
                    materias_grupos[clave] = {
                        'materia': {
                            'codigo': asig.materia.codigo_materia,
                            'nombre': asig.materia.nombre_materia,
                            'creditos': asig.materia.creditos
                        },
                        'grupo': asig.grupo.nombre_grupo,
                        'sesiones': []
                    }
                
                # Agregar información de la sesión si no existe ya
                sesion_info = {
                    'dia': asig.sesion.dia_semana,
                    'hora_inicio': asig.sesion.hora_inicio,
                    'hora_fin': asig.sesion.hora_fin,
                    'tipo': asig.sesion.tipo_sesion,
                    'docente': asig.sesion.docente,
                    'salon': asig.sesion.salon
                }
                
                if sesion_info not in materias_grupos[clave]['sesiones']:
                    materias_grupos[clave]['sesiones'].append(sesion_info)
            
            horario_export['horario'] = list(materias_grupos.values())
            return horario_export
            
        except Exception as e:
            logger.error(f"Error exportando horario: {e}")
            return {'error': str(e)}
    
    def importar_horario_json(self, datos_horario: Dict[str, any]) -> Dict[str, any]:
        """Importa un horario desde formato JSON"""
        try:
            # Limpiar horario actual
            self.limpiar_horario()
            
            # Procesar cada materia/grupo
            materias_importadas = 0
            errores = []
            
            for item in datos_horario.get('horario', []):
                codigo_materia = item['materia']['codigo']
                nombre_grupo = item['grupo']
                
                resultado = self.agregar_grupo_al_horario(codigo_materia, nombre_grupo)
                
                if resultado['exito']:
                    materias_importadas += 1
                else:
                    errores.append(f"{codigo_materia} - {nombre_grupo}: {resultado['mensaje']}")
            
            return {
                'exito': materias_importadas > 0,
                'materias_importadas': materias_importadas,
                'errores': errores,
                'mensaje': f'Se importaron {materias_importadas} grupos al horario'
            }
            
        except Exception as e:
            logger.error(f"Error importando horario: {e}")
            return {
                'exito': False,
                'mensaje': f'Error interno: {str(e)}',
                'errores': [str(e)]
            }


class AgregarGrupoCommand(Command):
    """Comando para agregar un grupo al horario."""
    def __init__(self, service: HorarioService, codigo_materia: str, nombre_grupo: str):
        super().__init__(service)
        self.codigo_materia = codigo_materia
        self.nombre_grupo = nombre_grupo

    def execute(self) -> Dict[str, Any]:
        # Validaciones previas
        materia = self.service.materia_repo.obtener_por_codigo(self.codigo_materia)
        if not materia: return {'exito': False, 'mensaje': 'Materia no encontrada.', 'tipo': 'error'}
        
        grupo = self.service.grupo_repo.obtener_por_materia_y_nombre(self.codigo_materia, self.nombre_grupo)
        if not grupo: return {'exito': False, 'mensaje': 'Grupo no encontrado.', 'tipo': 'error'}

        sesiones = self.service.sesion_repo.obtener_por_grupo(grupo.id_grupo_materia)
        if not sesiones: return {'exito': False, 'mensaje': 'Grupo sin sesiones.', 'tipo': 'warning'}

        conflictos = self.service._verificar_conflictos_horario(sesiones)
        if conflictos:
            msg = "Conflicto de horario:\n" + "\n".join([f"• {c['dia']} {c['hora']}: {c['materia_existente']}" for c in conflictos])
            return {'exito': False, 'mensaje': msg, 'tipo': 'conflict', 'conflictos': conflictos}

        return self.service._internal_agregar_grupo(self.codigo_materia, self.nombre_grupo)

    def undo(self) -> Dict[str, Any]:
        return self.service._internal_eliminar_grupo(self.codigo_materia, self.nombre_grupo)

class EliminarGrupoCommand(Command):
    """Comando para eliminar un grupo del horario."""
    def __init__(self, service: HorarioService, codigo_materia: str, nombre_grupo: str):
        super().__init__(service)
        self.codigo_materia = codigo_materia
        self.nombre_grupo = nombre_grupo

    def execute(self) -> Dict[str, Any]:
        return self.service._internal_eliminar_grupo(self.codigo_materia, self.nombre_grupo)

    def undo(self) -> Dict[str, Any]:
        return self.service._internal_agregar_grupo(self.codigo_materia, self.nombre_grupo)
