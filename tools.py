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
    "description": "View project files structure",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

write_file_tool = {
    "type": "function",
    "name": "write_file",
    "description": "Create a text file or overwrite existing content",
    "parameters": {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Filename to write with extension"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            }
        },
        "required": ["file_name", "content"]
    }
}

tools = [file_read_tool, directory_explore_tool, write_file_tool]