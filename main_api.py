import sys
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, Depends

# Add project root to the Python path
# This is necessary to ensure that modules like 'logica' and 'database' can be found
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from database.connection import DatabaseManager
from logica.services.materia_service import MateriaService

# --- App Definition ---
app = FastAPI(
    title="API de Horarios Udenar",
    description="API para gestionar la creación y consulta de horarios académicos.",
    version="0.1.0"
)

# --- Database Dependency ---
# Create a single instance of the DatabaseManager for the application's lifecycle
db_manager = DatabaseManager()

# Dependency function to get the database manager
# This can be used in path operations to get access to the db
def get_db_manager() -> DatabaseManager:
    # In a more complex app, you might get a session from a pool here
    # For this project, returning the single manager instance is sufficient
    return db_manager

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Endpoint de bienvenida que devuelve un mensaje de saludo.
    """
    return {"message": "Bienvenido a la API del proyecto de horarios"}

@app.get("/materias")
def obtener_materias(db: DatabaseManager = Depends(get_db_manager)):
    """
    Obtiene una lista de todas las materias con sus grupos y sesiones.
    """
    materia_service = MateriaService(db)
    materias = materia_service.obtener_todas_las_materias()
    return materias

# --- Lifecycle Events ---
@app.on_event("shutdown")
def shutdown_event():
    """
    Cierra la conexión a la base de datos cuando la aplicación se apaga.
    """
    db_manager.cerrar_conexion()
