import groq
from utils.config import settings
from sqlalchemy.orm import Session
from utils.tools import tools_schema, execute_tool_call

groq_client = groq.Client(api_key=settings.groq_api_key)


def run_agent_chat(user_message: str, user_id: int, db: Session) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI file manager and assistant. Use the provided tools to help the user with their account, files & questions.",
        },
        {"role": "user", "content": user_message},
    ]

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto",
        )

        response_message = completion.choices[0].message

        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                tool_result = execute_tool_call(tool_call, user_id, db)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": str(tool_result),
                    }
                )

            final_completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=tools_schema,
            )
            return final_completion.choices[0].message.content

        return response_message.content

    except Exception as e:
        print(f"Groq Agent Error: {e}")
        return "I'm sorry, I encountered an error while trying to process your request."


def generate_rag_answer(context_text: str, user_query: str) -> str:
    system_prompt = f"""
    You are a file manager assistant that can answer user queries about the file content 
    or answer questions for the user based on relevant context. 
    If the answer is not in the context, clearly state that you do not have enough information.
    Always cite the Source file name when providing information.

    CONTEXT:
    {context_text}
    """

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            max_tokens=1024,
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Groq API Error: {e}")
        raise
