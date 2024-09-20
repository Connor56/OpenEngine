# Use the official Qdrant image as the base
FROM qdrant/qdrant:v1.2.2

# Set environment variables to ensure non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install PostgreSQL: Add the PostgreSQL APT Repository
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    lsb-release \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-14 postgresql-client-14 \
    && rm -rf /var/lib/apt/lists/*

# Expose Qdrant and PostgreSQL ports
EXPOSE 6333 5432

# Create PostgreSQL data directory
RUN mkdir -p /var/lib/postgresql/data

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=openengine_user
ENV POSTGRES_PASSWORD=securepassword
ENV POSTGRES_DB=openengine_db

# Copy initialization script
COPY init-postgres.sh /docker-entrypoint-initdb.d/

# Start Qdrant and PostgreSQL
CMD ["bash", "-c", "service postgresql start && qdrant"]
