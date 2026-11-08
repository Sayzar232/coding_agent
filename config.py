import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH")