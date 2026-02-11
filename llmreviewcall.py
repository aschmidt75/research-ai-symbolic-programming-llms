from openrouter import OpenRouter
import logging
import os

DEFAULT_REVIEW_MODEL = os.getenv("OPENROUTER_REVIEW_MODEL", "anthropic/claude-opus-4.5")

def call_review_llm(prompt: str, model: str = DEFAULT_REVIEW_MODEL) -> object | None:
    logger = logging.getLogger("runner")
    with OpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY")
    ) as client:
        try:
            response = client.chat.send(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": ""
                    },
                    {
                        "role": "user",
                        "content": """
Rate the following block regarding the following aspects:

 does it purely contain symblic, math notation (x/10)
 how much prose does it contain (y/10)

```
"""
                        + prompt + """
```

output in JSON ONLY, matching the following pattern:

{
    "symbolic_rating": ###,
    "prose_rating": ###
}
"""

                    }
                ]
            )
        except Exception:
            logger.exception("Review LLM call failed for model %s", model)
            return None
        return response
