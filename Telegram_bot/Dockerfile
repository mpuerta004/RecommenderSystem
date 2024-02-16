FROM python:3.11.4

WORKDIR /

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
     poetry config virtualenvs.create false && \
     poetry install --no-dev  

ADD . /telegram_bot


# CMD  [ "poetry", "run", "python", "telegram_bot.py" ] 

# Develop option 
ENTRYPOINT ["tail", "-f", "/dev/null"] 