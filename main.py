from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from openai import BadRequestError
from pathlib import Path
import json

load_dotenv()

API_KEY = os.getenv("API_KEY")
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH")

file_read_tool = {
    "type": "function",
    "name": "read_file",
    "description": "Get text from a text file",
    "parameters": {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Filename to read with extension"
            }
        },
        "required": ["file_name"]
    }
}

directory_explore_tool = {
    "type": "function",
    "name": "view_files",
    "description": "View project files structure in json",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

tools = [file_read_tool, directory_explore_tool]

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

    def get_folder_structure(self, start_path=None) -> dict:
        if start_path is None:
            start_path = WORKSPACE_PATH if WORKSPACE_PATH else os.getcwd()

        structure = {}

        for item in os.listdir(start_path):
            item_path = os.path.join(start_path, item)

            if os.path.isdir(item_path):
                structure[item] = self.get_folder_structure(item_path)
            else:
                structure[item] = None

        return structure

    def get_file_content(self, file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            content = f.read()

        return content

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
                        folder_structure = self.get_folder_structure()
                        self.context.add_tool_call_output(
                            tool_id=step.id,
                            name=step.name,
                            content=json.dumps(folder_structure)
                        )
                    else:
                        raise ValueError(f"Unknown tool name: {step.name}")

agent = Agent()

agent.run()