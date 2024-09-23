import tempfile
import subprocess
import os

def start_ephemeral_postgres():
    # Create a temporary directory for the data
    temp_dir = tempfile.TemporaryDirectory()
    data_dir = os.path.join(temp_dir.name, 'data')

    # Initialize the database cluster with 'trust' authentication
    subprocess.run([
        'initdb',
        '-D', data_dir,
        '--auth=trust',
        '-U', 'postgres'
    ], check=True, stdout=subprocess.DEVNULL)

    # Start the PostgreSQL server using pg_ctl
    port = '54321'  # Use a non-standard port to avoid conflicts

    subprocess.run([
        'pg_ctl',
        '-D', data_dir,
        '-o', f'-p {port}',
        '-w', 'start'
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return temp_dir, port


def stop_ephemeral_postgres(temp_dir):
    # Stop the PostgreSQL server
    subprocess.run([
        'pg_ctl',
        '-D', os.path.join(temp_dir.name, 'data'),
        'stop',
        '-s', '-m', 'fast'
    ], check=True)
    temp_dir.cleanup()

# # Usage
# temp_dir, postgres_process, port = start_ephemeral_postgres()

# try:
#     # Connect to the temporary PostgreSQL server
#     conn = psycopg2.connect(
#         dbname='postgres',
#         user=os.getlogin(),
#         host=temp_dir.name,
#         port=port
#     )
#     cur = conn.cursor()

#     # Perform database operations
#     cur.execute("""
#         CREATE TABLE test_table (
#             id SERIAL PRIMARY KEY,
#             data TEXT
#         );
#     """)
#     conn.commit()

#     cur.execute("INSERT INTO test_table (data) VALUES (%s);", ('Sample data',))
#     conn.commit()

#     cur.execute("SELECT * FROM test_table;")
#     rows = cur.fetchall()
#     print(rows)  # Output: [(1, 'Sample data')]

#     # Cleanup
#     cur.close()
#     conn.close()
# finally:
#     stop_ephemeral_postgres(temp_dir, postgres_process)
