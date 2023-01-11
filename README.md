pip install mysql


cd Model 

sudo mysql -uroot -p < Model.BaseDatos.v6.sql




 
1. `pip install poetry` (or safer, follow the instructions: https://python-poetry.org/docs/#installation)
2. Install dependencies `cd` into the directory where the `pyproject.toml` is located then `poetry install`
3. sudo mysql -uroot -p < Model.BaseDatos.v6.sql
4. [UNIX]: Run the FastAPI server via poetry with the bash script: `poetry run ./run.sh`
5. [WINDOWS]: Run the FastAPI server via poetry with the Python command: `poetry run python src/Servicio/app/main.py`
6. Open http://localhost:8001/ <!---!> 






