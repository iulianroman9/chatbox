from sqlalchemy.orm import Session
from pathlib import Path
import json


def summarize_specific_file(file_id: int, user_id: int, db: Session) -> str:
    from api.services.file import get_file_by_id

    db_file = get_file_by_id(file_id, user_id, db)

    if not db_file:
        return f"Error: Could not find file with ID {file_id}. It may have been deleted or doesn't belong to you."

    file_path = Path(db_file.path)
    if not file_path.is_file():
        return f"Error: The physical file for '{db_file.original_name}' is missing from the server storage."

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        truncated_content = content[:15000]
        notice = ""
        if len(content) > 15000:
            notice = "\n\n[System Note: This document was very long, so only the first section was provided for the summary.]"
        return (
            f"--- Content of {db_file.original_name} ---\n{truncated_content}{notice}"
        )

    except Exception as e:
        return f"Error reading file {db_file.original_name}: {str(e)}"


def get_storage_usage(user_id: int, db: Session) -> str:
    from api.services.file import get_files_for_user

    db_files = get_files_for_user(user_id, db)

    if not db_files:
        return "You have 0 files uploaded and are currently using 0 MB of storage."

    file_count = len(db_files)
    total_bytes = sum(f.size for f in db_files)

    total_mb = round(total_bytes / (1024 * 1024), 2)

    return f"You currently have {file_count} files uploaded, consuming a total of {total_mb} MB of storage space."


def get_my_profile_info(user_id: int, db: Session) -> str:
    from api.services.user import get_user

    db_user = get_user(user_id, db)

    if not db_user:
        return "Error: Could not retrieve your profile information."

    created_date = (
        db_user.created_at.strftime("%Y-%m-%d") if db_user.created_at else "Unknown"
    )

    response_lines = [
        "Here is your current profile information:",
        f"* Name: {db_user.name or 'Not provided'}",
        f"* Email: {db_user.email}",
        f"* Phone: {db_user.phone or 'Not provided'}",
        f"* Member Since: {created_date}",
    ]

    return "\n".join(response_lines)


def list_my_files(user_id: int, db: Session) -> str:
    from api.services.file import get_files_for_user

    db_files = get_files_for_user(user_id, db)

    if not db_files:
        return "You currently have no files uploaded."

    response_lines = ["You have the following files uploaded:"]

    for f in db_files:
        size_kb = round(f.size / 1024, 2)

        response_lines.append(f"* {f.original_name} - {size_kb} KB (ID: {f.id})")

    return "\n".join(response_lines)


def get_api_status() -> str:
    return "The Chatbox API is running ok on version 0.1.0."


available_functions = {
    "get_api_status": get_api_status,
    "list_my_files": list_my_files,
    "get_my_profile_info": get_my_profile_info,
    "get_storage_usage": get_storage_usage,
    "summarize_specific_file": summarize_specific_file,
}


tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_api_status",
            "description": "Get the current status and version of the Chatbox API.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_my_files",
            "description": "Get a list of all documents and files the currently authenticated user has uploaded. Returns file names, IDs, and sizes.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_profile_info",
            "description": "Retrieve the currently authenticated user's account details, such as their name, email, phone, and account creation date.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_storage_usage",
            "description": "Get analytics on the user's file storage, specifically the total number of files they have uploaded and the total storage space used in Megabytes (MB).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_specific_file",
            "description": "Read the contents of a specific file to generate a summary or answer deep questions about it. You must provide the integer file_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "integer",
                        "description": "The unique ID of the file to summarize.",
                    }
                },
                "required": ["file_id"],
            },
        },
    },
]


def execute_tool_call(tool_call, user_id: int, db: Session):
    function_name = tool_call.function.name
    function_args = (
        json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
    )
    print(f"Executing {function_name} with args: {function_args}")

    if function_name == "get_api_status":
        return get_api_status()

    elif function_name == "list_my_files":
        return list_my_files(user_id=user_id, db=db)

    elif function_name == "get_my_profile_info":
        return get_my_profile_info(user_id=user_id, db=db)

    elif function_name == "get_storage_usage":
        return get_storage_usage(user_id=user_id, db=db)

    elif function_name == "summarize_specific_file":
        file_id = function_args.get("file_id")
        return summarize_specific_file(file_id=file_id, user_id=user_id, db=db)

    else:
        return f"Error: Function {function_name} not recognized."
