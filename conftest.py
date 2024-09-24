import pytest


@pytest.fixture(scope="function")
def empty_postgres_client():
    """
    A fixture that provides a psycopg2 client for testing and a the function for killing
    the server once the user is complete.
    """
    import psycopg2
    from setup_postgres import start_ephemeral_postgres, stop_ephemeral_postgres

    try:
        # Start a temporary PostgreSQL server
        print("starting postgres")
        temp_dir, port = start_ephemeral_postgres()

        # Connect to the temporary PostgreSQL server
        client = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            host="localhost",
            port=port
        )
        print("connected to postgres")

        cursor = client.cursor()

        # Create the table
        table_sql = """CREATE TABLE resources ( 
            id SERIAL PRIMARY KEY,
            url VARCHAR(2048) NOT NULL,
            firstVisited TIMESTAMPTZ NOT NULL,
            lastVisited TIMESTAMPTZ NOT NULL,
            allVisits INT DEFAULT 1,
            externalLinks TEXT[]
        );"""

        cursor.execute(table_sql)

        yield client

        client.close()

    except Exception as e:
        print(e)
        stop_ephemeral_postgres(temp_dir)

    finally:
        print("cleaning up")

        stop_ephemeral_postgres(temp_dir)


