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
import argparse
import docker

# Get the docker client
docker_client = docker.from_env()

# ==============================================================
# Get the args from argparse
# ==============================================================

parser = argparse.ArgumentParser()
parser.add_argument(
    "-rc",
    "--restart-containers",
    action="store_true",
    help="Restart the docker containers (WARNING: will delete any existing containers)",
)
parser.add_argument(
    "-kc",
    "--kill-containers",
    action="store_true",
    help="Kill the docker containers when the script ends",
)
parser.add_argument(
    "-f",
    "--frontend",
    action="store_true",
    help="Start the frontend in the script",
)

args = parser.parse_args()

print(args)

# ==============================================================
# Start the PostgreSQL server
# ==============================================================

postgres_name = "dev-postgres"

# Check if the postgres container exists
postgres_exists = (
    len(docker_client.containers.list(filters={"name": postgres_name})) > 0
)

# Shutdown any pre-existing container
if args.restart_containers:

    # Stop any container that exists
    subprocess.run(["docker", "stop", postgres_name])

    # Remove it from docker
    subprocess.run(["docker", "rm", postgres_name])


postgres_stopped = False

# Run the container
if args.restart_containers or not postgres_exists:
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

    # Check if the postgres container exists
    postgres_exists = (
        len(docker_client.containers.list(filters={"name": postgres_name})) > 0
    )

    # If the container doesn't exist, presumably the name is taken and it's
    # stopped but free to run
    if not postgres_exists:
        # Restart the stopped container
        print("Restarting stopped postgres container...")
        postgres_process = subprocess.run(["docker", "start", postgres_name])

        # Set postgres stopped to true
        postgres_stopped = True

        time.sleep(2)


async def setup_postgres():
    client = await asyncpg.connect(
        user="postgres", password="postgres", host="localhost", port=5432
    )

    print("connected to postgres")

    # Create the resource table
    resources_sql = """CREATE TABLE resources ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        firstVisited TIMESTAMP NOT NULL,
        lastVisited TIMESTAMP NOT NULL,
        allVisits INT DEFAULT 1,
        externalLinks TEXT[]
    );"""

    await client.execute(resources_sql)

    # Create the admin table
    admins_sql = """CREATE TABLE admins ( 
        id SERIAL PRIMARY KEY,
        username VARCHAR(2048) NOT NULL,
        password VARCHAR(2048) NOT NULL
    );"""

    await client.execute(admins_sql)

    # Create the seed urls table
    seed_urls_sql = """CREATE TABLE seed_urls ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        seeds VARCHAR(512)[]
    );"""

    await client.execute(seed_urls_sql)

    potential_urls_sql = """CREATE TABLE potential_urls ( 
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        firstSeen TIMESTAMP NOT NULL,
        timesSeen INT DEFAULT 1
    );"""

    await client.execute(potential_urls_sql)

    print("added all tables")


# Add the embeddings collection if they've been restarted
if args.restart_containers:
    asyncio.run(setup_postgres())

# Add the embeddings collection if the containers have been initially created
if not postgres_exists and not postgres_stopped:
    asyncio.run(setup_postgres())


# ==============================================================
# Start the qdrant server
# ==============================================================

qdrant_name = "dev-qdrant"

# Check if the qdrant container exists
qdrant_exists = (
    len(docker_client.containers.list(filters={"name": "dev-qdrant"})) > 0
)

# Shutdown any pre-existing container
if args.restart_containers:
    # Stop any container that exists
    subprocess.run(["docker", "stop", qdrant_name])

    # Remove it from docker
    subprocess.run(["docker", "rm", qdrant_name])

qdrant_stopeed = False

# Run the container
if args.restart_containers or not qdrant_exists:
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
    qdrant_exists = (
        len(docker_client.containers.list(filters={"name": qdrant_name})) > 0
    )

    # If the container doesn't exist, presumably the name is taken and it's
    # stopped but free to run
    if not qdrant_exists:
        # Start the stopped container
        qdrant_process = subprocess.run(["docker", "start", qdrant_name])

        # Set qdrant stopped to true
        qdrant_stopped = True

        time.sleep(2)

# Add the embeddings collection if the containers have been restarted
if args.restart_containers:
    created = qdrant.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    print("Embeddings collection created:", created)

    time.sleep(2)

# Add the embeddings collection if the containers have been initially created
if not qdrant_exists and not qdrant_stopped:
    created = qdrant.create_collection(
        collection_name="embeddings",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    print("Embeddings collection created:", created)

    time.sleep(2)

# ==============================================================
# Start the FastAPI backend
# ==============================================================

port = 54678

# Start the FastAPI backend
fastapi_process = subprocess.Popen(
    [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
        "--reload",
    ],
)

print("FastAPI backend process ID:", fastapi_process.pid)


# ==============================================================
# Set the static environment variable for the API URL
# ==============================================================

# Swap to the frontend directory
os.chdir("frontend/svelte-app")

# Open the env json
with open("static/env.json", "r") as f:
    data = json.load(f)

# Set the API URL
data["API_URL"] = f"http://localhost:{port}"

# Write the updated env json
with open("static/env.json", "w") as f:
    json.dump(data, f, indent=4)


# ==============================================================
# Start the frontend in dev mode
# ==============================================================

print("Starting frontend...")

# Check if platform is windows
platform_type = platform.system()

# Get a boolean flag
use_shell = platform_type == "Windows"

frontend_process = None

# Start the frontend
if args.frontend:
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        shell=use_shell,
    )

if frontend_process:
    print("Frontend process ID:", frontend_process.pid)


# ==============================================================
# Set up the interrupt and termination handlers
# ==============================================================


def handle_end(signal, frame):
    print("Received interrupt signal, terminating processes...")

    # Terminate the backend
    fastapi_process.terminate()

    if args.frontend:
        # Terminate the frontend
        frontend_process.terminate()

    if args.kill_containers:
        # Stop and remove the postgres docker container
        subprocess.run(["docker", "stop", postgres_name])
        subprocess.run(["docker", "rm", postgres_name])

        # Stop and remove the qdrant docker container
        subprocess.run(["docker", "stop", qdrant_name])
        subprocess.run(["docker", "rm", qdrant_name])

    # Set the .env dev to false

    print("Processes terminated.")

    exit(0)


signal.signal(signal.SIGINT, handle_end)
signal.signal(signal.SIGTERM, handle_end)

try:
    fastapi_process.wait()
except KeyboardInterrupt:
    print("Ending the process...")

    # Windows workaround
    handle_end(None, None)
