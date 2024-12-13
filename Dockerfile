FROM python:3.11-slim

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry
RUN poetry config virtualenvs.create false \
    && poetry export --only main --format requirements.txt > requirements.txt \
    && pip install --requirement requirements.txt \
    && rm requirements.txt

COPY ./src/ /app/src/

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Will be overriden by docker-compose
ENTRYPOINT [ "echo", "\"No entrypoint specified\""]
