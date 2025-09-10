
"""
Scripts de migración y inicialización de la base de datos
"""

import logging
from typing import List, Dict, Any
from database.connection import DatabaseManager

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Administrador de migraciones de la base de datos"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def ejecutar_migraciones(self) -> bool:
        """Ejecuta todas las migraciones necesarias"""
        try:
            with self.db_manager.transaccion() as conn:
                cursor = conn.cursor()
                
                # Crear tabla de migraciones si no existe
                self._crear_tabla_migraciones(cursor)
                
                # Obtener migraciones ejecutadas
                migraciones_ejecutadas = self._obtener_migraciones_ejecutadas(cursor)
                
                # Ejecutar migraciones pendientes
                migraciones = self._obtener_todas_las_migraciones()
                
                for version, migration in migraciones.items():
                    if version not in migraciones_ejecutadas:
                        logger.info(f"Ejecutando migración {version}: {migration['nombre']}")
                        
                        # Ejecutar la migración
                        migration['funcion'](cursor)
                        
                        # Registrar migración ejecutada
                        self._registrar_migracion(cursor, version, migration['nombre'])
                        
                        logger.info(f"Migración {version} completada exitosamente")
                
                # Poblar datos iniciales si es necesario
                if not migraciones_ejecutadas:
                    self._poblar_datos_iniciales(cursor)
                    logger.info("Datos iniciales poblados exitosamente")
                
                return True
                
        except Exception as e:
            logger.error(f"Error ejecutando migraciones: {e}")
            return False
    
    def _crear_tabla_migraciones(self, cursor):
        """Crea la tabla para tracking de migraciones"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migraciones (
                version TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                fecha_ejecucion DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
    def _obtener_migraciones_ejecutadas(self, cursor) -> set:
        """Obtiene las migraciones ya ejecutadas"""
        cursor.execute("SELECT version FROM migraciones")
        return {row[0] for row in cursor.fetchall()}
    
    def _registrar_migracion(self, cursor, version: str, nombre: str):
        """Registra una migración como ejecutada"""
        cursor.execute(
            "INSERT INTO migraciones (version, nombre) VALUES (?, ?)",
            (version, nombre)
        )
    
    def _obtener_todas_las_migraciones(self) -> Dict[str, Dict[str, Any]]:
        """Define todas las migraciones disponibles"""
        return {
            "001": {
                "nombre": "Crear tablas principales",
                "funcion": self._migration_001_crear_tablas
            }
        }
    
    def _migration_001_crear_tablas(self, cursor):
        """Migración 001: Crear las tablas principales del sistema"""
        
        # Tabla Materias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Materias (
                codigo_materia TEXT PRIMARY KEY,
                nombre_materia TEXT NOT NULL,
                creditos INTEGER
            );
        """)
        
        # Tabla GruposMateria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GruposMateria (
                id_grupo_materia INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_materia_fk TEXT NOT NULL,
                nombre_grupo TEXT NOT NULL,
                cupos INTEGER,
                FOREIGN KEY (codigo_materia_fk) REFERENCES Materias (codigo_materia) 
                    ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)
        
        # Tabla SesionesClase
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SesionesClase (
                id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_grupo_materia_fk INTEGER NOT NULL,
                tipo_sesion TEXT NOT NULL,
                dia_semana TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                docente TEXT,
                salon TEXT,
                FOREIGN KEY (id_grupo_materia_fk) REFERENCES GruposMateria (id_grupo_materia) 
                    ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)
        
        logger.info("Tablas principales creadas exitosamente")
    
    def _poblar_datos_iniciales(self, cursor):
        """Puebla la base de datos con datos iniciales"""
        from data.initial_data import MATERIAS_INICIALES
        
        logger.info("Poblando datos iniciales...")
        
        for materia_data in MATERIAS_INICIALES:
            # Insertar materia
            cursor.execute(
                "INSERT OR IGNORE INTO Materias (codigo_materia, nombre_materia, creditos) VALUES (?, ?, ?)",
                (materia_data["codigo"], materia_data["nombre"], 2)
            )
            
            # Insertar grupos y sesiones
            for grupo_data in materia_data["grupos"]:
                # Insertar grupo
                cursor.execute(
                    "INSERT INTO GruposMateria (codigo_materia_fk, nombre_grupo, cupos) VALUES (?, ?, ?)",
                    (materia_data["codigo"], grupo_data["nombre_grupo"], None)
                )
                
                grupo_id = cursor.lastrowid
                
                # Insertar sesiones del grupo
                for sesion_data in grupo_data["sesiones"]:
                    cursor.execute(
                        """INSERT INTO SesionesClase 
                           (id_grupo_materia_fk, tipo_sesion, dia_semana, hora_inicio, hora_fin, docente, salon) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            grupo_id,
                            grupo_data["tipo_sesion_predominante"],
                            sesion_data["dia"],
                            sesion_data["inicio"],
                            sesion_data["fin"],
                            grupo_data["docente"],
                            sesion_data["salon"]
                        )
                    )
        
        logger.info(f"Se insertaron {len(MATERIAS_INICIALES)} materias con sus grupos y sesiones")
    
    def verificar_integridad_datos(self) -> Dict[str, Any]:
        """Verifica la integridad de los datos en la base de datos"""
        try:
            with self.db_manager.cursor() as cursor:
                resultados = {
                    'materias_sin_grupos': [],
                    'grupos_sin_sesiones': [],
                    'sesiones_huerfanas': [],
                    'horarios_invalidos': []
                }
                
                # Materias sin grupos
                cursor.execute("""
                    SELECT m.codigo_materia, m.nombre_materia 
                    FROM Materias m 
                    LEFT JOIN GruposMateria g ON m.codigo_materia = g.codigo_materia_fk 
                    WHERE g.id_grupo_materia IS NULL
                """)
                resultados['materias_sin_grupos'] = cursor.fetchall()
                
                # Grupos sin sesiones
                cursor.execute("""
                    SELECT g.id_grupo_materia, g.nombre_grupo, g.codigo_materia_fk 
                    FROM GruposMateria g 
                    LEFT JOIN SesionesClase s ON g.id_grupo_materia = s.id_grupo_materia_fk 
                    WHERE s.id_sesion IS NULL
                """)
                resultados['grupos_sin_sesiones'] = cursor.fetchall()
                
                # Sesiones con horarios inválidos
                cursor.execute("""
                    SELECT id_sesion, dia_semana, hora_inicio, hora_fin 
                    FROM SesionesClase 
                    WHERE hora_inicio >= hora_fin
                """)
                resultados['horarios_invalidos'] = cursor.fetchall()
                
                return resultados
                
        except Exception as e:
            logger.error(f"Error verificando integridad: {e}")
            return {'error': str(e)}
