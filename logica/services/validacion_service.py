"""
Servicio de validaciones para el sistema de horarios
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, time

logger = logging.getLogger(__name__)

class ValidacionService:
    """Servicio centralizado para validaciones de datos"""
    
    # Expresiones regulares para validación
    REGEX_HORA = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    REGEX_CODIGO_MATERIA = re.compile(r'^[A-Z0-9_]{3,20}$')
    
    # Días válidos
    DIAS_VALIDOS = {'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'}
    
    # Tipos de sesión válidos
    TIPOS_SESION_VALIDOS = {'TEORICA', 'PRACTICA', 'LABORATORIO', 'SEMINARIO', 'TALLER'}
    
    def validar_codigo_materia(self, codigo: str) -> Dict[str, Any]:
        """Valida el formato de un código de materia"""
        resultado = {'es_valido': False, 'mensaje': '', 'sugerencias': []}
        
        if not codigo or not isinstance(codigo, str):
            resultado['mensaje'] = 'El código de materia no puede estar vacío'
            resultado['sugerencias'].append('Proporcione un código válido')
            return resultado
        
        codigo = codigo.strip().upper()
        
        if len(codigo) < 3:
            resultado['mensaje'] = 'El código debe tener al menos 3 caracteres'
            resultado['sugerencias'].append('Use códigos como: MATH101, CS201, etc.')
            return resultado
        
        if len(codigo) > 20:
            resultado['mensaje'] = 'El código no puede exceder 20 caracteres'
            return resultado
        
        if not self.REGEX_CODIGO_MATERIA.match(codigo):
            resultado['mensaje'] = 'El código solo puede contener letras, números y guiones bajos'
            resultado['sugerencias'].append('Formato válido: letras mayúsculas, números y _ solamente')
            return resultado
        
        resultado['es_valido'] = True
        resultado['mensaje'] = 'Código válido'
        resultado['codigo_normalizado'] = codigo
        return resultado
    
    def validar_nombre_materia(self, nombre: str) -> Dict[str, Any]:
        """Valida el nombre de una materia"""
        resultado = {'es_valido': False, 'mensaje': '', 'sugerencias': []}
        
        if not nombre or not isinstance(nombre, str):
            resultado['mensaje'] = 'El nombre de la materia no puede estar vacío'
            return resultado
        
        nombre = nombre.strip()
        
        if len(nombre) < 3:
            resultado['mensaje'] = 'El nombre debe tener al menos 3 caracteres'
            return resultado
        
        if len(nombre) > 100:
            resultado['mensaje'] = 'El nombre no puede exceder 100 caracteres'
            return resultado
        
        # Verificar caracteres válidos (letras, números, espacios, acentos, algunos símbolos)
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-\.\/\(\)\&]+$', nombre):
            resultado['mensaje'] = 'El nombre contiene caracteres no válidos'
            resultado['sugerencias'].append('Use solo letras, números, espacios y símbolos básicos')
            return resultado
        
        resultado['es_valido'] = True
        resultado['mensaje'] = 'Nombre válido'
        resultado['nombre_normalizado'] = nombre.upper()
        return resultado
    
    def validar_creditos(self, creditos: Optional[int]) -> Dict[str, Any]:
        """Valida la cantidad de créditos"""
        resultado = {'es_valido': True, 'mensaje': '', 'sugerencias': []}
        
        if creditos is None:
            resultado['mensaje'] = 'Créditos no especificados (se usará valor por defecto)'
            return resultado
        
        if not isinstance(creditos, int):
            try:
                creditos = int(creditos)
            except (ValueError, TypeError):
                resultado['es_valido'] = False
                resultado['mensaje'] = 'Los créditos deben ser un número entero'
                return resultado
        
        if creditos < 0:
            resultado['es_valido'] = False
            resultado['mensaje'] = 'Los créditos no pueden ser negativos'
            return resultado
        
        if creditos > 10:
            resultado['mensaje'] = 'Cantidad de créditos inusualmente alta'
            resultado['sugerencias'].append('Verifique que el valor sea correcto')
        elif creditos == 0:
            resultado['mensaje'] = 'Materia sin créditos'
            resultado['sugerencias'].append('Confirme si es correcto para este tipo de materia')
        
        resultado['creditos_validados'] = creditos
        return resultado
    
    def validar_hora(self, hora: str) -> Dict[str, Any]:
        """Valida el formato de una hora HH:MM"""
        resultado = {'es_valido': False, 'mensaje': '', 'sugerencias': []}
        
        if not hora or not isinstance(hora, str):
            resultado['mensaje'] = 'La hora no puede estar vacía'
            return resultado
        
        hora = hora.strip()
        
        if not self.REGEX_HORA.match(hora):
            resultado['mensaje'] = 'Formato de hora inválido. Use HH:MM'
            resultado['sugerencias'].append('Ejemplos válidos: 08:00, 14:30, 19:45')
            return resultado
        
        # Validar que la hora sea lógica para un horario académico
        try:
            hora_obj = datetime.strptime(hora, "%H:%M").time()
            
            if hora_obj < time(6, 0):
                resultado['mensaje'] = 'Hora muy temprana para actividades académicas'
                resultado['sugerencias'].append('Considere horarios entre 06:00 y 22:00')
            elif hora_obj > time(22, 0):
                resultado['mensaje'] = 'Hora muy tardía para actividades académicas'
                resultado['sugerencias'].append('Considere horarios entre 06:00 y 22:00')
            else:
                resultado['es_valido'] = True
                resultado['mensaje'] = 'Hora válida'
        
        except ValueError:
            resultado['mensaje'] = 'Error procesando la hora'
        
        resultado['hora_normalizada'] = hora
        return resultado
    
    def validar_rango_horario(self, hora_inicio: str, hora_fin: str) -> Dict[str, Any]:
        """Valida un rango de horario (inicio y fin)"""
        resultado = {'es_valido': False, 'mensaje': '', 'sugerencias': []}
        
        # Validar horas individuales
        val_inicio = self.validar_hora(hora_inicio)
        val_fin = self.validar_hora(hora_fin)
        
        if not val_inicio['es_valido']:
            resultado['mensaje'] = f'Hora de inicio inválida: {val_inicio["mensaje"]}'
            return resultado
        
        if not val_fin['es_valido']:
            resultado['mensaje'] = f'Hora de fin inválida: {val_fin["mensaje"]}'
            return resultado
        
        try:
            inicio_obj = datetime.strptime(hora_inicio, "%H:%M")
            fin_obj = datetime.strptime(hora_fin, "%H:%M")
            
            if inicio_obj >= fin_obj:
                resultado['mensaje'] = 'La hora de inicio debe ser anterior a la hora de fin'
                resultado['sugerencias'].append('Verifique el orden de las horas')
                return resultado
            
            # Calcular duración
            duracion = fin_obj - inicio_obj
            duracion_horas = duracion.total_seconds() / 3600
            
            if duracion_horas < 0.5:
                resultado['mensaje'] = 'Duración muy corta (menos de 30 minutos)'
                resultado['sugerencias'].append('Las sesiones académicas suelen durar al menos 1 hora')
            elif duracion_horas > 4:
                resultado['mensaje'] = 'Duración muy larga (más de 4 horas)'
                resultado['sugerencias'].append('Considere dividir en sesiones más cortas')
            else:
                resultado['es_valido'] = True
                resultado['mensaje'] = 'Rango horario válido'
            
            resultado['duracion_horas'] = duracion_horas
            
        except ValueError as e:
            resultado['mensaje'] = f'Error procesando el rango horario: {str(e)}'
        
        return resultado
    
    def validar_dia_semana(self, dia: str) -> Dict[str, Any]:
        """Valida un día de la semana"""
        resultado = {'es_valido': False, 'mensaje': '', 'sugerencias': []}
        
        if not dia or not isinstance(dia, str):
            resultado['mensaje'] = 'El día de la semana no puede estar vacío'
            return resultado
        
        dia_normalizado = dia.strip().capitalize()
        
        if dia_normalizado not in self.DIAS_VALIDOS:
            resultado['mensaje'] = 'Día de la semana no válido'
            resultado['sugerencias'] = list(self.DIAS_VALIDOS)
            return resultado
        
        resultado['es_valido'] = True
        resultado['mensaje'] = 'Día válido'
        resultado['dia_normalizado'] = dia_normalizado
        return resultado
    
    def validar_tipo_sesion(self, tipo: str) -> Dict[str, Any]:
        """Valida el tipo de sesión"""
        resultado = {'es_valido': False, 'mensaje': '', 'sugerencias': []}
        
        if not tipo or not isinstance(tipo, str):
            resultado['mensaje'] = 'El tipo de sesión no puede estar vacío'
            return resultado
        
        tipo_normalizado = tipo.strip().upper()
        
        if tipo_normalizado not in self.TIPOS_SESION_VALIDOS:
            resultado['mensaje'] = 'Tipo de sesión no válido'
            resultado['sugerencias'] = list(self.TIPOS_SESION_VALIDOS)
            return resultado
        
        resultado['es_valido'] = True
        resultado['mensaje'] = 'Tipo de sesión válido'
        resultado['tipo_normalizado'] = tipo_normalizado
        return resultado
    
    def validar_sesion_completa(self, datos_sesion: Dict[str, Any]) -> Dict[str, Any]:
        """Valida todos los datos de una sesión completa"""
        resultado = {
            'es_valida': True,
            'errores': [],
            'advertencias': [],
            'datos_normalizados': {}
        }
        
        # Validar tipo de sesión
        if 'tipo_sesion' in datos_sesion:
            val_tipo = self.validar_tipo_sesion(datos_sesion['tipo_sesion'])
            if not val_tipo['es_valido']:
                resultado['errores'].append(f"Tipo de sesión: {val_tipo['mensaje']}")
                resultado['es_valida'] = False
            else:
                resultado['datos_normalizados']['tipo_sesion'] = val_tipo['tipo_normalizado']
        
        # Validar día
        if 'dia_semana' in datos_sesion:
            val_dia = self.validar_dia_semana(datos_sesion['dia_semana'])
            if not val_dia['es_valido']:
                resultado['errores'].append(f"Día: {val_dia['mensaje']}")
                resultado['es_valida'] = False
            else:
                resultado['datos_normalizados']['dia_semana'] = val_dia['dia_normalizado']
        
        # Validar horario
        if 'hora_inicio' in datos_sesion and 'hora_fin' in datos_sesion:
            val_horario = self.validar_rango_horario(datos_sesion['hora_inicio'], datos_sesion['hora_fin'])
            if not val_horario['es_valido']:
                resultado['errores'].append(f"Horario: {val_horario['mensaje']}")
                resultado['es_valida'] = False
            else:
                resultado['datos_normalizados']['hora_inicio'] = datos_sesion['hora_inicio']
                resultado['datos_normalizados']['hora_fin'] = datos_sesion['hora_fin']
                resultado['datos_normalizados']['duracion_horas'] = val_horario.get('duracion_horas', 0)
        
        # Validar campos opcionales
        if 'docente' in datos_sesion and datos_sesion['docente']:
            if len(datos_sesion['docente'].strip()) < 3:
                resultado['advertencias'].append('Nombre de docente muy corto')
            else:
                resultado['datos_normalizados']['docente'] = datos_sesion['docente'].strip()
        
        if 'salon' in datos_sesion and datos_sesion['salon']:
            resultado['datos_normalizados']['salon'] = datos_sesion['salon'].strip()
        
        return resultado
