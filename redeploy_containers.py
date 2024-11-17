import subprocess
import os
import json
import time
import signal
import asyncpg
import asyncio
import platform
import qdrant_client
from qdrant_client.models import VectorParams, Distance
import docker

# Get the docker client
docker_client = docker.from_env()

# ==============================================================
# Start the PostgreSQL server
# ==============================================================

postgres_name = "dev-postgres"

# Check if the postgres container exists
postgres_exists = (
    len(docker_client.containers.list(filters={"name": postgres_name})) > 0
)

# Stop any container that exists
subprocess.run(["docker", "stop", postgres_name])

# Remove it from docker
subprocess.run(["docker", "rm", postgres_name])


postgres_stopped = False

# Run the container

# Start the PostgreSQL server
print("Starting new postgres container...")
postgres_process = subprocess.run(
    [
        "docker",
        "run",
        "--name",
        postgres_name,
        "-e",
        "POSTGRES_PASSWORD=postgres",
        "-p",
        "5432:5432",
        "-d",
        "postgres",
    ],
)

time.sleep(2)

from setup import setup_postgres

# Add the embeddings collection if they've been restarted
asyncio.run(setup_postgres())


# ==============================================================
# Start the qdrant server
# ==============================================================

qdrant_name = "dev-qdrant"

# Check if the qdrant container exists
qdrant_exists = len(docker_client.containers.list(filters={"name": "dev-qdrant"})) > 0

# Stop any container that exists
subprocess.run(["docker", "stop", qdrant_name])

# Remove it from docker
subprocess.run(["docker", "rm", qdrant_name])

qdrant_stopeed = False

# Run the container

# Start the server in docker
qdrant_process = subprocess.run(
    [
        "docker",
        "run",
        "--name",
        qdrant_name,
        "-p",
        "6333:6333",
        "-d",
        "qdrant/qdrant",
    ],
)

qdrant = qdrant_client.QdrantClient(host="localhost", port=6333)

time.sleep(2)

# Check the qdrant container exists
qdrant_exists = len(docker_client.containers.list(filters={"name": qdrant_name})) > 0

from setup import setup_qdrant

asyncio.run(setup_qdrant(qdrant))

time.sleep(2)
