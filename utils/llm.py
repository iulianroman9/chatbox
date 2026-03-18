import groq
from utils.config import settings

groq_client = groq.Client(api_key=settings.groq_api_key)


def generate_rag_answer(context_text: str, user_query: str) -> str:
    system_prompt = f"""
    You are a file manager assistant that can answer user queries about the file content 
    or answer questions for the user based on relevant context. 
    If the answer is not in the context, clearly state that you do not have enough information.
    Always cite the Source file name when providing information.
    WRITE PLAINTEXT NOT MARKDOWN

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
