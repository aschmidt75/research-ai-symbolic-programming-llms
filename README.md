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


## Usage

To run the experiments, you need to have Python installed. Then, you can run the following command:

```bash
uv run main.py
```

This will run the experiments using the models defined in [models.json](./models.json) and the request defined in [request.txt](./request.txt). The results will be saved in the `results` directory.


