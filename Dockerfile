FROM python:3.10.15-slim

WORKDIR /app

# keep requirements files on top so that it mostly uses cached ones as docker build images layer by layer and if
# any single layer changes all the forward layers are invalidated and build again
COPY /pyproject.toml /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install

COPY . .

# cmd command is run when container starts
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
# CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --reload --host 0.0.0.0 --port 8080"]

# the settings.host value tells us the address the app will bind to.
# If settings.host is set to 127.0.0.1, the app will only accept connections from within the container itself.
# This is because 127.0.0.1 is the loopback address, which means it's only accessible from the same container.
# Docker containers have their own isolated network environments, and each container has its own localhost (127.0.0.1) that isn't shared with the host machine or other containers. So, if you bind your app to 127.0.0.1, it won't be accessible from outside the container.
# To make your Fastapi app accessible from outside the container, you need to set settings.host to 0.0.0.0.
# This tells the app to listen on all available network interfaces, including the one Docker uses to route
# external traffic to the container.
