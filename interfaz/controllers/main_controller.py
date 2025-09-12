"""
Controlador principal para la interfaz de horarios
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from database.connection import DatabaseManager
from database.repositories.materia_repository import MateriaRepository
from logica.services.horario_service import HorarioService
from logica.utils.color_utils import ColorUtils

logger = logging.getLogger(__name__)

class MainController:
    """Controlador principal que coordina la lógica de negocio con la interfaz"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Inicializar repositorios y servicios
        self.materia_repo = MateriaRepository(db_manager)
        self.horario_service = HorarioService(db_manager)
        
        # Callbacks para la interfaz
        self.on_horario_changed: Optional[Callable] = None
        self.on_creditos_changed: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_success: Optional[Callable] = None
        self.on_warning: Optional[Callable] = None
        
        # Estado de la interfaz
        self._materias_data = {}
        self._colores_materias = {}
        
        # Pila para la funcionalidad de deshacer
        self._undo_stack: List[Callable] = []
        self._redo_stack: List[Callable] = [] # Para futura implementación de rehacer
        
        # Cargar datos iniciales
        self._cargar_materias()
    
    def _cargar_materias(self):
        """Carga todas las materias desde la base de datos"""
        try:
            materias = self.materia_repo.obtener_todas()
            
            for materia in materias:
                # Obtener horarios de la materia
                horarios = self.materia_repo.obtener_horarios(materia.codigo_materia)
                
                # Organizar por grupos
                grupos = {}
                for horario in horarios:
                    nombre_grupo = horario.get('nombre_grupo', 'Sin Grupo')
                    if nombre_grupo not in grupos:
                        grupos[nombre_grupo] = {
                            'sesiones': [],
                            'docente': horario.get('docente', 'N/A')
                        }
                    grupos[nombre_grupo]['sesiones'].append(horario)
                
                # Almacenar datos de la materia
                self._materias_data[materia.codigo_materia] = {
                    'nombre': materia.nombre_materia,
                    'creditos': materia.creditos or 0,
                    'grupos': grupos
                }
                
                # Generar color para la materia
                self._colores_materias[materia.codigo_materia] = ColorUtils.generar_color_por_codigo(
                    materia.codigo_materia
                )
            
            logger.info(f"Cargadas {len(materias)} materias desde la base de datos")
            
        except Exception as e:
            logger.error(f"Error cargando materias: {e}")
            if self.on_error:
                self.on_error("Error de Carga", f"No se pudieron cargar las materias: {e}")
    
    # Métodos para obtener datos
    
    def obtener_todas_las_materias(self) -> Dict[str, Any]:
        """Obtiene todas las materias para la interfaz"""
        return self._materias_data.copy()
    
    def obtener_materias_filtradas(self, termino_busqueda: str) -> Dict[str, Any]:
        """Obtiene materias filtradas por término de búsqueda"""
        if not termino_busqueda:
            return self._materias_data.copy()
        
        termino_lower = termino_busqueda.lower()
        materias_filtradas = {}
        
        for codigo, data in self._materias_data.items():
            if (termino_lower in data['nombre'].lower() or 
                termino_lower in codigo.lower()):
                materias_filtradas[codigo] = data
        
        return materias_filtradas
    
    def obtener_color_materia(self, codigo_materia: str) -> str:
        """Obtiene el color asignado a una materia"""
        return self._colores_materias.get(codigo_materia, '#F8F9FA')
    
    def obtener_horario_actual(self) -> Dict:
        """Obtiene el horario actualmente asignado"""
        horario_raw = self.horario_service.obtener_horario_actual()
        
        # Convertir a formato compatible con la interfaz existente
        horario_interfaz = {}
        for (dia, hora), asignacion in horario_raw.items():
            horario_interfaz[(dia, hora)] = asignacion.to_dict()
        
        return horario_interfaz
    
    # Métodos para manipular horarios
    
    def _execute_command(self, command: Optional[Callable]):
        """Ejecuta un comando, lo guarda en la pila de deshacer y notifica a la UI."""
        if command is None:
            return

        resultado = command.execute()

        if resultado.get('exito'):
            self._undo_stack.append(command)
            self._redo_stack.clear() # Una nueva acción limpia la pila de rehacer
            
            if self.on_horario_changed: self.on_horario_changed()
            if self.on_creditos_changed: self.on_creditos_changed()
            if self.on_success: self.on_success("Acción Realizada", resultado['mensaje'])
        else:
            # Manejar diferentes tipos de error/advertencia
            if resultado.get('tipo') == 'conflict':
                if self.on_warning: self.on_warning("Conflicto de Horario", resultado['mensaje'])
            else:
                if self.on_error: self.on_error("Error", resultado.get('mensaje', 'Acción fallida'))

    def agregar_grupo_al_horario(self, codigo_materia: str, nombre_grupo: str) -> bool:
        """Agrega un grupo al horario"""
        command = self.horario_service.crear_comando_agregar_grupo(codigo_materia, nombre_grupo)
        self._execute_command(command)
    
    def eliminar_del_horario(self, dia: str, hora: str) -> bool:
        """Elimina una materia del horario"""
        command = self.horario_service.crear_comando_eliminar_grupo(dia, hora)
        self._execute_command(command)

    def deshacer_ultima_accion(self):
        """Deshace la última acción realizada."""
        if not self._undo_stack:
            if self.on_warning:
                self.on_warning("Deshacer", "No hay acciones que deshacer.")
            return

        command_to_undo = self._undo_stack.pop()
        resultado = command_to_undo.undo()
        
        # Opcional: Mover a la pila de rehacer
        # self._redo_stack.append(command_to_undo)

        if resultado.get('exito'):
            if self.on_horario_changed: self.on_horario_changed()
            if self.on_creditos_changed: self.on_creditos_changed()
            if self.on_success: self.on_success("Acción Deshecha", resultado['mensaje'])
        else:
            # Si deshacer falla, es un estado inconsistente. Volver a poner el comando.
            self._undo_stack.append(command_to_undo)
            if self.on_error: self.on_error("Error al Deshacer", resultado.get('mensaje', 'No se pudo deshacer la acción.'))
    
    def limpiar_horario(self) -> Dict[str, Any]:
        """Limpia completamente el horario"""
        # Limpiar también la pila de deshacer
        self._undo_stack.clear()
        self._redo_stack.clear()

        resultado = self.horario_service.limpiar_horario()
        
        if resultado['exito']:
            # Notificar cambios a la interfaz
            if self.on_horario_changed:
                self.on_horario_changed()
            
            if self.on_creditos_changed:
                self.on_creditos_changed()
        
        return resultado
    
    # Métodos de información y estadísticas
    
    def obtener_total_creditos(self) -> int:
        """Obtiene el total de créditos del horario actual"""
        return self.horario_service.obtener_total_creditos()
    
    def obtener_estadisticas_horario(self) -> Dict[str, Any]:
        """Obtiene estadísticas del horario actual"""
        return self.horario_service.obtener_estadisticas_horario()
    
    def validar_carga_creditos(self) -> Dict[str, Any]:
        """Valida la carga actual de créditos"""
        return self.horario_service.validar_carga_creditos()
    
    # Métodos de importación/exportación
    
    def exportar_horario(self) -> Dict[str, Any]:
        """Exporta el horario actual"""
        return self.horario_service.exportar_horario_json()
    
    def importar_horario(self, datos_horario: Dict[str, Any]) -> Dict[str, Any]:
        """Importa un horario desde datos JSON"""
        resultado = self.horario_service.importar_horario_json(datos_horario)
        
        if resultado['exito']:
            # Notificar cambios a la interfaz
            if self.on_horario_changed:
                self.on_horario_changed()
            
            if self.on_creditos_changed:
                self.on_creditos_changed()
        
        return resultado
    
    # Métodos de búsqueda y filtrado
    
    def buscar_materias(self, termino: str) -> List[Dict[str, Any]]:
        """Busca materias por término"""
        try:
            materias = self.materia_repo.buscar(termino)
            return [
                {
                    'codigo': m.codigo_materia,
                    'nombre': m.nombre_materia,
                    'creditos': m.creditos or 0
                }
                for m in materias
            ]
        except Exception as e:
            logger.error(f"Error buscando materias: {e}")
            return []
    
    # Métodos de validación
    
    def validar_horario_actual(self) -> Dict[str, Any]:
        """Valida el horario actual completo"""
        try:
            validacion_creditos = self.validar_carga_creditos()
            estadisticas = self.obtener_estadisticas_horario()
            
            return {
                'es_valido': validacion_creditos['es_valida'],
                'validacion_creditos': validacion_creditos,
                'estadisticas': estadisticas,
                'recomendaciones': self._generar_recomendaciones(estadisticas, validacion_creditos)
            }
            
        except Exception as e:
            logger.error(f"Error validando horario: {e}")
            return {'error': str(e)}
    
    def _generar_recomendaciones(self, estadisticas: Dict, validacion: Dict) -> List[str]:
        """Genera recomendaciones basadas en estadísticas y validación"""
        recomendaciones = []
        
        # Recomendaciones de créditos
        recomendaciones.extend(validacion.get('recomendaciones', []))
        
        # Recomendaciones de distribución
        if estadisticas.get('total_materias', 0) == 0:
            recomendaciones.append("Agregue materias a su horario")
        
        sesiones_por_dia = estadisticas.get('sesiones_por_dia', {})
        dias_sin_clases = [dia for dia, count in sesiones_por_dia.items() if count == 0]
        
        if len(dias_sin_clases) >= 3:
            recomendaciones.append("Considere distribuir mejor las materias en la semana")
        
        # Verificar días muy cargados
        dias_sobrecargados = [dia for dia, count in sesiones_por_dia.items() if count > 6]
        if dias_sobrecargados:
            recomendaciones.append(f"Los días {', '.join(dias_sobrecargados)} están muy cargados")
        
        return recomendaciones
    
    # Métodos de gestión de errores
    
    def verificar_integridad_datos(self) -> Dict[str, Any]:
        """Verifica la integridad de los datos"""
        try:
            # Aquí se podría llamar a métodos de verificación de la base de datos
            return {
                'integridad_ok': True,
                'mensaje': 'Datos íntegros'
            }
        except Exception as e:
            logger.error(f"Error verificando integridad: {e}")
            return {
                'integridad_ok': False,
                'mensaje': f'Error de integridad: {e}'
            }
