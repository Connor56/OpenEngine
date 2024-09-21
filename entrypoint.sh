#!/bin/bash
set -e

# Start PostgreSQL
echo "Starting PostgreSQL..."
service postgresql start

# Wait for PostgreSQL to be fully initialized (optional, but recommended)
until pg_isready -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Start Qdrant
echo "Starting Qdrant..."
exec ./qdrant
