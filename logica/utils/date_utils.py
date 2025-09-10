"""
Utilidades para manejo de fechas y horas
"""

from datetime import datetime, time, timedelta
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DateUtils:
    """Utilidades para manejo de fechas y horas en el sistema de horarios"""
    
    # Mapeo de días en español
    DIAS_ESPANOL = {
        'monday': 'Lunes',
        'tuesday': 'Martes', 
        'wednesday': 'Miércoles',
        'thursday': 'Jueves',
        'friday': 'Viernes',
        'saturday': 'Sábado',
        'sunday': 'Domingo'
    }
    
    DIAS_SEMANA_ORDEN = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    @staticmethod
    def validar_formato_hora(hora_str: str) -> bool:
        """Valida si una hora tiene el formato correcto HH:MM"""
        try:
            datetime.strptime(hora_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def convertir_hora_a_minutos(hora_str: str) -> int:
        """Convierte una hora HH:MM a minutos desde medianoche"""
        try:
            hora_obj = datetime.strptime(hora_str, "%H:%M")
            return hora_obj.hour * 60 + hora_obj.minute
        except ValueError as e:
            logger.error(f"Error convirtiendo hora {hora_str} a minutos: {e}")
            return 0
    
    @staticmethod
    def convertir_minutos_a_hora(minutos: int) -> str:
        """Convierte minutos desde medianoche a formato HH:MM"""
        horas = minutos // 60
        mins = minutos % 60
        return f"{horas:02d}:{mins:02d}"
    
    @staticmethod
    def calcular_duracion_sesion(hora_inicio: str, hora_fin: str) -> float:
        """Calcula la duración de una sesión en horas"""
        try:
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fin = datetime.strptime(hora_fin, "%H:%M")
            
            # Manejar caso donde la sesión cruza medianoche
            if fin < inicio:
                fin += timedelta(days=1)
            
            duracion = fin - inicio
            return duracion.total_seconds() / 3600
            
        except ValueError as e:
            logger.error(f"Error calculando duración entre {hora_inicio} y {hora_fin}: {e}")
            return 0.0
    
    @staticmethod
    def generar_horas_entre_rango(hora_inicio: str, hora_fin: str) -> List[str]:
        """Genera lista de horas enteras entre un rango"""
        horas = []
        
        try:
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fin = datetime.strptime(hora_fin, "%H:%M")
            
            current = inicio
            while current < fin:
                horas.append(current.strftime("%H:%M"))
                current += timedelta(hours=1)
                
        except ValueError as e:
            logger.error(f"Error generando horas entre {hora_inicio} y {hora_fin}: {e}")
        
        return horas
    
    @staticmethod
    def obtener_orden_dia(dia: str) -> int:
        """Obtiene el orden numérico de un día de la semana (0=Lunes)"""
        try:
            return DateUtils.DIAS_SEMANA_ORDEN.index(dia)
        except ValueError:
            return 999  # Para días no reconocidos
    
    @staticmethod
    def es_dia_laborable(dia: str) -> bool:
        """Verifica si un día es laborable (Lunes a Viernes)"""
        return dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    @staticmethod
    def es_horario_academico_valido(hora: str) -> bool:
        """Verifica si una hora está en rango académico típico (6:00 - 22:00)"""
        try:
            hora_obj = datetime.strptime(hora, "%H:%M").time()
            return time(6, 0) <= hora_obj <= time(22, 0)
        except ValueError:
            return False
    
    @staticmethod
    def formatear_rango_horario(hora_inicio: str, hora_fin: str) -> str:
        """Formatea un rango horario para mostrar"""
        return f"{hora_inicio} - {hora_fin}"
    
    @staticmethod
    def hay_solapamiento_horario(inicio1: str, fin1: str, inicio2: str, fin2: str) -> bool:
        """Verifica si dos rangos horarios se solapan"""
        try:
            i1 = DateUtils.convertir_hora_a_minutos(inicio1)
            f1 = DateUtils.convertir_hora_a_minutos(fin1)
            i2 = DateUtils.convertir_hora_a_minutos(inicio2)
            f2 = DateUtils.convertir_hora_a_minutos(fin2)
            
            return max(i1, i2) < min(f1, f2)
            
        except Exception as e:
            logger.error(f"Error verificando solapamiento: {e}")
            return False
    
    @staticmethod
    def generar_horarios_disponibles(dia: str, horarios_ocupados: List[Tuple[str, str]], 
                                   hora_inicio_busqueda: str = "07:00",
                                   hora_fin_busqueda: str = "19:00",
                                   duracion_minima: int = 60) -> List[Tuple[str, str]]:
        """Genera horarios disponibles en un día dado"""
        disponibles = []
        
        try:
            inicio_busqueda = DateUtils.convertir_hora_a_minutos(hora_inicio_busqueda)
            fin_busqueda = DateUtils.convertir_hora_a_minutos(hora_fin_busqueda)
            
            # Convertir horarios ocupados a minutos y ordenar
            ocupados_minutos = []
            for inicio, fin in horarios_ocupados:
                ocupados_minutos.append((
                    DateUtils.convertir_hora_a_minutos(inicio),
                    DateUtils.convertir_hora_a_minutos(fin)
                ))
            
            ocupados_minutos.sort()
            
            # Buscar gaps disponibles
            ultimo_fin = inicio_busqueda
            
            for inicio_ocupado, fin_ocupado in ocupados_minutos:
                if inicio_ocupado - ultimo_fin >= duracion_minima:
                    # Hay espacio disponible
                    disponibles.append((
                        DateUtils.convertir_minutos_a_hora(ultimo_fin),
                        DateUtils.convertir_minutos_a_hora(inicio_ocupado)
                    ))
                ultimo_fin = max(ultimo_fin, fin_ocupado)
            
            # Verificar espacio después del último ocupado
            if fin_busqueda - ultimo_fin >= duracion_minima:
                disponibles.append((
                    DateUtils.convertir_minutos_a_hora(ultimo_fin),
                    DateUtils.convertir_minutos_a_hora(fin_busqueda)
                ))
        
        except Exception as e:
            logger.error(f"Error generando horarios disponibles: {e}")
        
        return disponibles
