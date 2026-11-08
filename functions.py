import os
from config import WORKSPACE_PATH


def get_folder_structure(start_path=None) -> dict:
    if start_path is None:
        start_path = WORKSPACE_PATH if WORKSPACE_PATH else os.getcwd()

    structure = {}

    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)

        if os.path.isdir(item_path):
            structure[item] = get_folder_structure(item_path)
        else:
            structure[item] = None

    return structure if structure else "No files found in the directory."


def get_file_content(file_name):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content


def write_file_content(file_name, content):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)