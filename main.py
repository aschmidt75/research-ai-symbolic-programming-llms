from llmcall import call_llm
from response_writer import write_response
import json

def main() -> None:
    output_root_dir = "../0_symbolic-results"
    with open("request.txt", "r", encoding="utf-8") as request_file:
        prompt = request_file.read()
    with open("models.json", "r", encoding="utf-8") as models_file:
        models = json.load(models_file)
    for model_key, model_name in models.items():
        response = call_llm(prompt, model_name)
        output_path = write_response(output_root_dir, model_key, response)
        print(f"{model_key}: {output_path}")
        #print(response.choices[0].message.content)
        

if __name__ == "__main__":
    main()
