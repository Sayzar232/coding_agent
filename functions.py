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

    return structure


def get_file_content(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    return content