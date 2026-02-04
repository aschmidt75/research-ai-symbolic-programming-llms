import json
import os

def write_response(output_root_dir: str, model_key: str, response: object) -> str:
    model_dir = os.path.join(output_root_dir, model_key)
    os.makedirs(model_dir, exist_ok=True)
    if hasattr(response, "model_dump"):
        response_payload = response.model_dump()
    elif hasattr(response, "to_dict"):
        response_payload = response.to_dict()
    else:
        response_payload = response
    existing_files = [
        filename
        for filename in os.listdir(model_dir)
        if filename.startswith("res-") and filename.endswith(".json")
    ]
    existing_indices = []
    for filename in existing_files:
        index_part = filename.removeprefix("res-").removesuffix(".json")
        if index_part.isdigit():
            existing_indices.append(int(index_part))
    file_index = (max(existing_indices) + 1) if existing_indices else 1
    output_path = os.path.join(model_dir, f"res-{file_index:03d}.json")
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(response_payload, output_file, ensure_ascii=False, indent=2, default=str)
    
    output_text_path = output_path.removesuffix(".json") + ".txt"
    response_text = response.choices[0].message.content
    with open(output_text_path, "w", encoding="utf-8") as output_text_file:
        output_text_file.write(response_text)

    return output_path
