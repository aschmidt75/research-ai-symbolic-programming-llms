# research-ai-symbolic-programming-llms

This repository contains the codebase for the automation of research on symbolic programmming using LLMs.

A sample request is provided in [request.txt](./request.txt). It contains set of symbolic types and inference rules for weather, street, and traction states. Either 
- it's raining or it's not raining,
- the street is dry or it's wet,
- the traction is stable or it's slippery.
Inference rules state that only if its raining, the street will be wet, and if the street is wet, the traction will be slippery.
The request contains two different contexts, ω and v, which are used to derive the street and traction states based on the weather state, along with desired outputs.
The last requested output is the question whether the street being wet implies that it is raining.

[models.json](./models.json) defines a map of LLM backends, available through [OpenRouter](https://openrouter.ai/). Per associated backend, reasoning and optionally other parameters can be specified.

## Research

The setup aims to answer the following questions:
- Which models can understand symbolic notation and can operate on it successfully?
- Is there a difference between reasoning models and non-reasoning models?

Targeted LLMs are
- OpenAI
    - GPT5.2 (openai/gpt-5.2)
    - openai/gpt-oss-120b
    - openai/gpt-oss-20b
- Anthropic
    - Opus 4.5 (anthropic/claude-opus-4.5)
    - Sonnet 4.5 (anthropic/claude-sonnet-4.5)
    - Haiku 4.5 (anthropic/claude-haiku-4.5)
- Google
    - Gemini 3 Pro (google/gemini-3-pro-preview)
    - Gemini 3 Flash (google/gemini-3-flash-preview)
    - Gemma 3 4B (google/gemma-3n-e4b-it)
- Meta
    - Llama 4 Maverick (meta-llama/llama-4-maverick)
    - Llama 3.1 32B Instruct (meta-llama/llama-3.2-3b-instruct)
    - Llama 3.2 1B Instruct (meta-llama/llama-3.2-1b-instruct)
- Qwen
    - Qwen 3 Max (qwen/qwen3-max)
    - Qwen 3 Coder (qwen/qwen3-coder)
    - Qwen 3 32B (qwen/qwen3-32b)
- DeepSeek
    - DeepSeek V3.2 (deepseek/deepseek-v3.2)
- Mistral AI
    - Mistral Large 3 (mistralai/mistral-large-2512)
    - Mistral Small (mistralai/mistral-small-3.2-24b-instruct)
    - Ministral 3 8B (mistralai/ministral-8b-2512)
- xAI   
    - Grok-4 Fast reasoning (x-ai/grok-4.1-fast)
- NVidia
    - nvidia/nemotron-3-nano-30b-a3b
    - nvidia/nemotron-nano-12b-v2-vl:free
    - nvidia/nemotron-nano-9b-v2:free

## Usage

To run the experiments, you need to have Python installed. Then, you can run the following command:

```bash
uv run main.py
```

This will run the experiments using the models defined in [models.json](./models.json) and the request defined in [request.txt](./request.txt). The results will be saved in the `results` directory.


