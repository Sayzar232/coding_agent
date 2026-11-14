import os
import subprocess
from config import WORKSPACE_PATH


def get_folder_structure(start_path=None) -> dict:
    if start_path is None:
        start_path = WORKSPACE_PATH if WORKSPACE_PATH else os.getcwd()

    structure = {}

    try:
        items = os.listdir(start_path)
        for item in items:
            item_path = os.path.join(start_path, item)

            if os.path.isdir(item_path):
                structure[item] = get_folder_structure(item_path)
            else:
                structure[item] = None

        return structure if structure else "No files found in the directory."

    except FileNotFoundError:
        return f"Directory '{start_path}' not found."
    except Exception as e:
        return f"Error accessing directory '{start_path}': {e}"


def get_file_content(file_name):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name
    content = ""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for count, line in enumerate(f.readlines()):
                content += f"{count + 1}. {line}"
    except FileNotFoundError:
        content = f"File '{file_name}' not found."
    except Exception as e:
        content = f"Error reading file '{file_name}': {e}"

    return content


def write_file_content(file_name, content):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Error writing to file '{file_name}': {e}")


def create_directory(directory_name):
    directory_path = os.path.join(WORKSPACE_PATH, directory_name) if WORKSPACE_PATH else directory_name

    try:
        os.makedirs(directory_path, exist_ok=True)
    except Exception as e:
        raise IOError(f"Error creating directory '{directory_name}': {e}")


def edit_file_part(file_name, start_line, end_line, new_content):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name

    if start_line < 1 or end_line < start_line:
        raise ValueError("Expected 1 <= start_line <= end_line")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_name}' not found.")
    except Exception as e:
        raise IOError(f"Error reading file '{file_name}': {e}")

    if end_line > len(lines):
        raise ValueError(f"File '{file_name}' only has {len(lines)} lines")

    replacement = new_content.splitlines(keepends=True)
    if replacement and not replacement[-1].endswith(("\n", "\r")):
        replacement[-1] += "\n"

    lines[start_line - 1:end_line] = replacement

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception as e:
        raise IOError(f"Error writing to file '{file_name}': {e}")


def execute_powershell_command(command):
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command,
            ],
            cwd=WORKSPACE_PATH or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        if result.returncode != 0:
            output += f"\nReturn code: {result.returncode}"

        return output or "(command produced no output)"
    except subprocess.TimeoutExpired:
        return "Command exceeded time limit (30 seconds)"
    except OSError as e:
        return f"Failed to execute PowerShell command: {e}"