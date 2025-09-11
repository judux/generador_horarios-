import uvicorn
from fastapi import FastAPI
from database.connection import DatabaseManager
from interfaz.controllers.main_controller import MainController
from logica.dto.materia_dto import MateriaDTO

app = FastAPI()

# Initialize DatabaseManager and MainController
db_manager = DatabaseManager()
main_controller = MainController(db_manager)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Horarios API"}

@app.get("/api/materias", response_model=list[MateriaDTO])
async def get_all_materias():
    """
    Endpoint para obtener todas las materias disponibles, incluyendo grupos y sesiones.
    """
    return main_controller.obtener_todas_las_materias_dto()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
