import os
import subprocess
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
    content = ""

    with open(file_path, "r", encoding="utf-8") as f:
        for count, line in enumerate(f.readlines()):
            content += f"{count + 1}. {line}"

    return content


def write_file_content(file_name, content):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def create_directory(directory_name):
    directory_path = os.path.join(WORKSPACE_PATH, directory_name) if WORKSPACE_PATH else directory_name
    os.makedirs(directory_path, exist_ok=True)


def edit_file_part(file_name, start_line, end_line, new_content):
    file_path = os.path.join(WORKSPACE_PATH, file_name) if WORKSPACE_PATH else file_name

    if start_line < 1 or end_line < start_line:
        raise ValueError("Ожидается 1 <= start_line <= end_line")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if end_line > len(lines):
        raise ValueError(f"В файле только {len(lines)} строк")

    replacement = new_content.splitlines(keepends=True)
    if replacement and not replacement[-1].endswith(("\n", "\r")):
        replacement[-1] += "\n"

    lines[start_line - 1:end_line] = replacement

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

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
            output += f"\nКод завершения: {result.returncode}"

        return output or "(команда ничего не вывела)"
    except subprocess.TimeoutExpired:
        return "Команда превысила лимит времени (30 секунд)"
    except OSError as e:
        return f"Не удалось запустить PowerShell: {e}"