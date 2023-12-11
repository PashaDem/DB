FROM python:3.11-slim

ENV DST=/cleanix \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.4.2

WORKDIR ${DST}

RUN pip3 install "poetry==$POETRY_VERSION"

COPY ./poetry.lock ./pyproject.toml ${DST}/

RUN poetry install --only main --no-root

#source
COPY . ${DST}

CMD ["python3", "main.py"]