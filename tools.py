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