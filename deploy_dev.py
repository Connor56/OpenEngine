import subprocess
import os
import json
import time
import signal
import asyncpg
import asyncio

# ==============================================================
# Start the PostgreSQL server
# ==============================================================

postgres_name = "dev-postgres"

# Stop any container that exists
subprocess.run(["docker", "stop", postgres_name])

# Remove it from docker
subprocess.run(["docker", "rm", postgres_name])

# Start the PostgreSQL server
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


asyncio.run(setup_postgres())


# ==============================================================
# Start the qdrant server
# ==============================================================

qdrant_name = "dev-qdrant"

# Stop any container that exists
subprocess.run(["docker", "stop", qdrant_name])

# Remove it from docker
subprocess.run(["docker", "rm", qdrant_name])

# Start the server in memory
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

time.sleep(2)

# ==============================================================
# Start the FastAPI backend
# ==============================================================

port = 54678

# Start the FastAPI backend
fastapi_process = subprocess.Popen(
    ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
)

print(fastapi_process.pid)


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

# Start the frontend
frontend_process = subprocess.Popen(
    ["npm", "run", "dev"],
)

print(frontend_process.pid)


# ==============================================================
# Set up the interrupt and termination handlers
# ==============================================================


def handle_end(signal, frame):
    print("Received interrupt signal, terminating processes...")

    # Terminate the backend
    fastapi_process.terminate()

    # Terminate the frontend
    frontend_process.terminate()

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

fastapi_process.wait()
