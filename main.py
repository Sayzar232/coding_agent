from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import BadRequestError
from pathlib import Path

load_dotenv()

API_KEY = os.getenv("API_KEY")

file_read_tool = {
    "type": "function",
    "function": {
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
}

directory_explore_tool = {
    "type": "function",
    "function": {
        "name": "view_files",
        "description": "View project files and folders",
    }
}

tools = [file_read_tool, directory_explore_tool]

class AgentContext:
    def __init__(self):
        self.context = []

    def __getitem__(self, key):
        return self.context[key]

    def __iter__(self):
        return iter(self.context)

    def add(self, other):
        self.context.append(other)


class Agent:
    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.context = AgentContext()
        self.loop = True

    def get_folder_files(self):
        file_structure = ""
        folder = Path('.')

        files = [f for f in folder.iterdir()]

        for file in files:
            file_structure = file_structure + file.name + "\n"

    def request_chat(self):
        try:
            output = self.client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=self.context.context,
                tools=tools
            )
        except BadRequestError as e:
            print("Ошибка API:", e)
            print("Подробности:", e.response.text)
            raise
        return output

    def run(self):
        user_input = input("User: ")

        self.context.add({
            "role": "user",
            "content": user_input
        })

        while self.loop:
            response = self.request_chat()

            for choice in response.choices:
                if not choice.message.tool_calls:
                    self.loop = False
                    continue

                for tool_call in choice.message.tool_calls:
                    if tool_call.function.name == "view_files":
                        print("called view_files")
                    elif tool_call.function.name == "read_file":
                        print("called read_file")

            message = response.choices[0].message.content

            print(message)

            self.loop = False

agent = Agent()

agent.run()