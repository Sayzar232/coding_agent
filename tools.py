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

create_directory_tool = {
    "type": "function",
    "name": "create_directory",
    "description": "Create a new directory",
    "parameters": {
        "type": "object",
        "properties": {
            "directory_name": {
                "type": "string",
                "description": "Name of the directory to create"
            }
        },
        "required": ["directory_name"]
    }
}

edit_file_part = {
    "type": "function",
    "name": "edit_file_part",
    "description": "Edit a specific part of a text file",
    "parameters": {
        "type": "object",
        "properties": {
            "file_name": {
                "type": "string",
                "description": "Filename to edit with extension"
            },
            "start_line": {
                "type": "integer",
                "description": "The line number to start editing from (1-indexed)"
            },
            "end_line": {
                "type": "integer",
                "description": "The line number to end editing at (1-indexed)"
            },
            "content": {
                "type": "string",
                "description": "New content to replace the existing content"
            }
        },
        "required": ["file_name", "content"]
    }
}

tools = [file_read_tool, directory_explore_tool, write_file_tool, create_directory_tool, edit_file_part]