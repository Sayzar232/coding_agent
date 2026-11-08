from google import genai
from google.genai import types
import os
from openai import BadRequestError
from pathlib import Path
import json
from tools import tools
from functions import get_folder_structure, get_file_content
from config import API_KEY


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

    def add_tool_call(self, tool_id, name, arguments):
        self.history.append({
            "role": "assistant",
            "tool_calls": [{
                "id": tool_id,
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": arguments
                }
            }]
        })

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

    def request_chat(self):
        try:
            response = self.client.interactions.create(
                model="gemini-3.5-flash-lite",
                input=self.context.history,
                tools=tools
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

            for step in response.steps:
                if step.type == "function_call":
                    if step.name == "view_files":
                        folder_structure = get_folder_structure()
                        self.context.add_tool_call_output(
                            tool_id=step.id,
                            name=step.name,
                            content=json.dumps(folder_structure)
                        )
                        print("Вызов функции 'view_files'")
                    elif step.name == "read_file":
                        file_name = step.arguments.get("file_name")
                        print("Вызов функции 'read_file'")
                        if file_name:
                            try:
                                content = get_file_content(file_name)
                                self.context.add_tool_call_output(
                                    tool_id=step.id,
                                    name=step.name,
                                    content=content
                                )
                            except FileNotFoundError:
                                self.context.add_tool_call_output(
                                    tool_id=step.id,
                                    name=step.name,
                                    content=f"File '{file_name}' not found."
                                )
                        else:
                            self.context.add_tool_call_output(
                                tool_id=step.id,
                                name=step.name,
                                content="No file name provided."
                            )
                    else:
                        raise ValueError(f"Unknown tool name: {step.name}")