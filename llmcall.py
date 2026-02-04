from openrouter import OpenRouter
import os

def call_llm(prompt: str, model: str, reasoning: bool) -> str:
    with OpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY")
    ) as client:
        request_params = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": ""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        if reasoning:
            request_params["reasoning"] = {
                "effort": "medium"
            }
        response = client.chat.send(**request_params)
        return response
