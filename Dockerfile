FROM python:3.8.10

WORKDIR /

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev  

ADD . /recommendersystem

CMD  [ "poetry", "run", "python", "/recommendersystem/src/Servicio/app/main.py" ]

# ENTRYPOINT ["tail", "-f", "/dev/null"]