FROM python:3.11.4

WORKDIR /

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev  

ADD . /recommendersystem


CMD  [ "poetry", "run", "python", "/recommendersystem/src/Servicio/app/main.py" ] 

# Develop option 
# ENTRYPOINT ["tail", "-f", "/dev/null"] 