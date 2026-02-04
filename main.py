from llmcall import call_llm
from llmreviewcall import call_review_llm
from response_writer import write_response
import json


def main() -> None:
    output_root_dir = "../0_symbolic-results"
    with open("request.txt", "r", encoding="utf-8") as request_file:
        prompt = request_file.read()
    with open("models.json", "r", encoding="utf-8") as models_file:
        models = json.load(models_file)
    for model_key, model_config in models.items():
        model_name = model_config["m"]
        use_reasoning = model_config.get("r", False)
        response = call_llm(prompt, model_name, use_reasoning)
        review_prompt = response.choices[0].message.content
        review_response = call_review_llm(review_prompt)
        review_json = review_response.choices[0].message.content
        
        output_path = write_response(output_root_dir, model_key, response, review_json)
        print(f"{model_key}: {output_path}")
        #print(response.choices[0].message.content)
        

if __name__ == "__main__":
    main()
