FROM python:3.12.7-slim

# Python
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.3

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# # Install psycopg2 otherwise it will fail while attempting to build from source
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Copy project files
COPY pyproject.toml poetry.lock /app/
COPY app /app/app

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev --no-ansi

EXPOSE 5555

CMD ["poetry", "run", "start-flask"]