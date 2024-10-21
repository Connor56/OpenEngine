import os
import subprocess
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
import shutil


# --------------------------------------------------------------
# Build the Svelte App
# --------------------------------------------------------------

# Get the current working directory
current_dir = os.getcwd()

# Change to the frontend directory
os.chdir("frontend/svelte-app")

# Build the frontend
# subprocess.run(["npm", "run", "build"])


# --------------------------------------------------------------
# Deploy the static site frontend for nginx
# --------------------------------------------------------------

# Enter the build directory
os.chdir("build")


def extract_all_files(directory: str) -> List[str]:
    """
    Recursively extracts all files from a provided directory.
    """
    return [str(file) for file in Path(directory).rglob("*") if file.is_file()]


def get_all_link_hrefs(file: str) -> List[str]:
    """
    Extracts all link hrefs from a provided file.
    """
    links = []

    with open(file, "r") as f:

        soup = BeautifulSoup(f, "html.parser")

        for link in soup.select("link"):
            links.append(link.attrs["href"][2:])

    return links


def get_required_files(search_list: List[str]) -> List[str]:
    """
    Extracts all required files from a provided list of search files.
    """
    required_files = []

    for file in search_list:
        required_files += get_all_link_hrefs(file)

    return required_files


def copy_file_with_structure(
    src_file: str,
    src_base_dir: str,
    dest_base_dir: str,
):
    """
    Copies a file from a source directory to a destination directory
    while maintaining the directory structure.
    """
    # Get the relative path of the file from the source base directory
    relative_path = os.path.relpath(src_file, src_base_dir)

    # Construct the full destination path
    dest_file = os.path.join(dest_base_dir, relative_path)

    # Create the destination directory if it doesn't exist
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

    # Copy the file to the destination
    shutil.copy2(src_file, dest_file)


all_files = extract_all_files("./")

# Get the compiled svelte files needed for these static pages
search_files = ["index.html", "login.html", "results.html"]

required_files = get_required_files(search_files)

# Limit the required files to those in the directory
required_files = [file for file in required_files if file in all_files]
required_files += search_files

# Base dir
base_dir = current_dir + "/static_site"

for file in required_files:
    copy_file_with_structure(file, "./", base_dir)


# --------------------------------------------------------------
# Deploy the FastAPI authentication protected backend
# --------------------------------------------------------------

# Get the compiled svelte files needed for these static pages
search_files = ["set-admin.html", "admin.html"]

required_files = get_required_files(search_files)

# Limit the required files to those in the directory
required_files = [file for file in required_files if file in all_files]
required_files += search_files

# Base dir
base_dir = current_dir + "/app/backend_files"

for file in required_files:
    copy_file_with_structure(file, "./", base_dir)
