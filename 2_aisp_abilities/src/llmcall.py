from openrouter import OpenRouter
from pathlib import Path
import logging
import os

_SRC_DIR = Path(__file__).parent
_AISP_SPEC_FILE = _SRC_DIR / "aisp51.aisp"
_REQUEST_SPEC_FILE = _SRC_DIR / "request.spec.aisp"


def _load_system_content() -> str:
    parts: list[str] = []
    for path in (_AISP_SPEC_FILE, _REQUEST_SPEC_FILE):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                parts.append(text)
        except FileNotFoundError:
            logging.getLogger("runner").warning("System-content file not found: %s", path)
    return "\n\n".join(parts)


def call_llm(prompt: str, model: str, reasoning: bool) -> object | None:
    logger = logging.getLogger("runner")
    system_content = _load_system_content()
    with OpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY")
    ) as client:
        request_params = {
            "model": model,
            "max_tokens": 16384,
            "messages": [
                {
                    "role": "system",
                    "content": system_content
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
