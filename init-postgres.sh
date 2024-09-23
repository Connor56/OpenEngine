#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
    CREATE DATABASE $POSTGRES_DB;
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOSQL

# Connect to the newly created database and create the URLVisits table
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE resources (
        id SERIAL PRIMARY KEY,
        url VARCHAR(2048) NOT NULL,
        firstVisited TIMESTAMPTZ NOT NULL,
        lastVisited TIMESTAMPTZ NOT NULL,
        allVisits INT DEFAULT 1,
        externalLinks TEXT[]
    );
EOSQL
