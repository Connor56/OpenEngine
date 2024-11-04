# OpenEngine

OpenEngine is a web crawler and search engine that uses the [Qdrant](https://qdrant.tech/) vector database to store and search for websites. It is designed to conquer the niches of the internet. One man can't compete with the scale of the tech elite. But scale gives rise to its own problems. For example, Google's algorithm is consistently gamed by marketing firms that put terrible blog content at the top of every search. Truly interesting, unique, and valuable information is lost in a sea of regurgitated bullshit noise.

Step in OpenEngine. OpenEngine is designed to be run on a cheap, small docker container in the cloud. It is not designed to serve billions of requests a day, but to let interested individuals build their own curated indexes in niches they find cool and serve that information to their community as a service.

# Deployment

## Local Deployment

You can deploy locally with the `deploy_dev.py` script, first by starting poetry:

```sh
poetry install --no-root
```

This installs all the python packages for the project. Then by starting a poetry shell:

```sh
poetry shell
```

This starts a shell with all the packages installed. Then finally running the dev deployment script:

```sh
python deploy_dev.py
```

This will start the postgres and qdrant servers, start the FastAPI backend, and start the frontend in dev mode. The script starts everything as a subprocess and pipes all the output from Uvicorn and the vite dev server to the terminal. You can stop the process by pressing `Ctrl + C`.
