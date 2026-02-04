from openrouter import OpenRouter
import os

def call_llm(prompt: str, model: str) -> str:
    with OpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY")
    ) as client:
        response = client.chat.send(
            model=model,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        return response
