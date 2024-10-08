import tempfile
import subprocess
import os
from typing import Tuple


def start_ephemeral_postgres() -> Tuple[tempfile.TemporaryDirectory, str]:
    """
    Creates a temporary directory for a postgres database and starts
    the postgres server.

    Returns
    -------
    Tuple[tempfile.TemporaryDirectory, str]
        A tuple containing the temporary directory and the port the
        postgres server is running on.
    """
    # Create a temporary directory for the data
    temp_dir = tempfile.TemporaryDirectory()
    data_dir = os.path.join(temp_dir.name, "data")

    # Initialize the database cluster with 'trust' authentication
    subprocess.run(
        ["initdb", "-D", data_dir, "--auth=trust", "-U", "postgres"],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    # Start the PostgreSQL server using pg_ctl
    port = "54321"  # Use a non-standard port to avoid conflicts

    subprocess.run(
        ["pg_ctl", "-D", data_dir, "-o", f"-p {port}", "-w", "start"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return temp_dir, port


def stop_ephemeral_postgres(temp_dir: tempfile.TemporaryDirectory):
    """
    Uses the temporary directory and port from
    start_ephemeral_postgres to stop the postgres server.

    Parameters
    ----------
    temp_dir : tempfile.TemporaryDirectory
        The temporary directory created by start_ephemeral_postgres.
    """
    # Stop the PostgreSQL server
    subprocess.run(
        [
            "pg_ctl",
            "-D",
            os.path.join(temp_dir.name, "data"),
            "stop",
            "-s",
            "-m",
            "fast",
        ],
        check=True,
    )
    temp_dir.cleanup()
