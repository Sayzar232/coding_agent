from google import genai
from google.genai import types
import os
from openai import BadRequestError
from pathlib import Path
import json
from tools import tools
from functions import get_folder_structure, get_file_content, write_file_content, create_directory, edit_file_part, execute_powershell_command
from config import API_KEY, SYSTEM_PROMPT


class AgentContext:
    def __init__(self):
        self.history = []

    def __getitem__(self, key):
        return self.history[key]

    def __iter__(self):
        return iter(self.history)

    def add_user_text(self, other):
        prompt = {
            "type": "user_input",
            "content": [
                {
                    "type": "text",
                    "text": other
                }
            ]
        }
        self.history.append(prompt)

    def add_tool_call_output(self, tool_id, name, content):
        self.history.append(
            {
                "type": "function_result",
                "name": name,
                "call_id": tool_id,
                "result": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            }
        )

    def add(self, item):
        self.history.append(item)

    def extend(self, items):
        self.history.extend(items)


class Agent:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)
        self.context = AgentContext()
        self.loop = True
        self.tools_dict = {
            "read_file": self.handle_read_file_tool,
            "view_files": self.handle_view_files_tool,
            "write_file": self.handle_write_file_tool,
            "create_directory": self.handle_create_directory_tool,
            "edit_file_part": self.handle_edit_file_part_tool,
            "run_command": self.handle_run_command_tool
        }

    def request_chat(self):
        try:
            response = self.client.interactions.create(
                model="gemini-3.5-flash-lite",
                input=self.context.history,
                tools=tools,
                system_instruction=SYSTEM_PROMPT
            )
        except BadRequestError as e:
            print("Ошибка API:", e)
            print("Подробности:", e.response.text)
            raise
        return response

    def _is_function_call(self, response):
        is_function_call = False
        for step in response.steps:
            if step.type == "function_call":
                is_function_call = True
                break
        return is_function_call

    def print_tool_call(self, step):
        print(f"Вызов функции '{step.name}'")
        print("Аргументы:")
        for key, value in step.arguments.items():
            value = str(value)
            if len(value) > 64:
                value = value[:64] + "..."
            print(f"  {key}: {value}")

    def handle_view_files_tool(self, step):
        self.print_tool_call(step)

        folder_structure = get_folder_structure()

        self.context.add_tool_call_output(
            tool_id=step.id,
            name=step.name,
            content=json.dumps(folder_structure)
        )

    def handle_read_file_tool(self, step):
        self.print_tool_call(step)

        file_name = step.arguments.get("file_name")

        try:
            content = get_file_content(file_name)
        except Exception as e:
            content = f"Error reading file '{file_name}': {e}"

        self.context.add_tool_call_output(
            tool_id=step.id,
            name=step.name,
            content=content
        )

    def handle_write_file_tool(self, step):
        self.print_tool_call(step)
        file_name = step.arguments.get("file_name")
        content = step.arguments.get("content")

        try:
            write_file_content(file_name, content)
            output_message = f"File '{file_name}' written successfully."
        except Exception as e:
            output_message = f"Error writing to file '{file_name}': {e}"

        self.context.add_tool_call_output(
            tool_id=step.id,
            name=step.name,
            content=output_message
        )

    def handle_create_directory_tool(self, step):
        self.print_tool_call(step)

        directory_name = step.arguments.get("directory_name")

        try:
            create_directory(directory_name)
            output_message = f"Directory '{directory_name}' created successfully."
        except Exception as e:
            output_message = f"Error creating directory '{directory_name}': {e}"

        self.context.add_tool_call_output(
            tool_id=step.id,
            name=step.name,
            content=output_message
        )

    def handle_edit_file_part_tool(self, step):
        self.print_tool_call(step)
        file_name = step.arguments.get("file_name")
        start_line = step.arguments.get("start_line")
        end_line = step.arguments.get("end_line")
        new_content = step.arguments.get("content")

        try:
            edit_file_part(file_name, start_line, end_line, new_content)
            output_message = f"File '{file_name}' edited successfully from line {start_line} to {end_line}."    
        except Exception as e:
            output_message = f"Error editing file '{file_name}': {e}"

        self.context.add_tool_call_output(
            tool_id=step.id,
            name=step.name,
            content=output_message
        )

    def handle_run_command_tool(self, step):
        self.print_tool_call(step)
        command = step.arguments.get("command")

        try:
            output = execute_powershell_command(command)
            output_message = f"Command executed successfully. Output:\n{output}"
        except Exception as e:
            output_message = f"Error executing command '{command}': {e}"

        self.context.add_tool_call_output(
            tool_id=step.id,
            name=step.name,
            content=output_message
        )

    def handle_tools(self, response):
        for step in response.steps:
            if step.type == "function_call":
                if step.name not in self.tools_dict:
                    raise ValueError(f"Unknown tool name: {step.name}")

                self.tools_dict[step.name](step)

    def run(self):
        user_input = input("User: ")

        self.context.add_user_text(user_input)

        while self.loop:
            response = self.request_chat()

            self.context.extend(response.steps)

            message = response.output_text
            print(message)

            if not self._is_function_call(response):
                user_input = input("User: ")
                self.context.add_user_text(user_input)

            self.handle_tools(response)