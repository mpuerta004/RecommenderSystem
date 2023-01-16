 
1. `pip install poetry` (or safer, follow the instructions: https://python-poetry.org/docs/#installation)
2. Install dependencies `cd` into the directory where the `pyproject.toml` is located then `poetry install`
3. [UNIX] Run `cd Model` 
4. [UNIX] Run `sudo mysql -uroot -p < BaseDatos.v6.sql`
5. [UNIX] Run `cd ..`
6. [UNIX]: Run the FastAPI server via poetry with the bash script: `poetry run ./run.sh`
6. [WINDOWS]: Run the FastAPI server via poetry with the Python command: `poetry run python src/Servicio/app/main.py`
7. Open http://localhost:8001/ <!---!> 


Use case - Example: 

1. We have to create the hive. At http://localhost:8001 in secction Hives at the endpoint post. 
![plot](./Picture_readme/Hive_section.PNG)
Click on Post endpoint and then in "Try it out" botton and complete the Request body (pìcture example) and click execute 
![plot](./Picture_readme/Hive_post.PNG)
And we can see the created hive: 
![plot](./Picture_readme/hive_zaragoza.PNG)
)







