from openrouter import OpenRouter
import logging
import os

def call_llm(prompt: str, model: str, reasoning: bool) -> object | None:
    logger = logging.getLogger("runner")
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
        else:
            request_params["reasoning"] = {
                "effort": "none",
                "enabled": False
            }
        logger.debug("Request params: %s", request_params)
        try:
            response = client.chat.send(**request_params)
        except Exception:
            logger.exception("LLM call failed for model %s", model)
            return None
            
        return response
