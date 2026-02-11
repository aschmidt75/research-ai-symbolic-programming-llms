from llmcall import call_llm
from llmreviewcall import call_review_llm
from response_writer import write_response
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
import argparse
import json
import logging


def setup_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run configured models and persist results.")
    parser.add_argument("-m", "--model", default=None, help="Model key from models.json to run.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.debug)
    logger = logging.getLogger("runner")
    output_root_dir = "../0_symbolic-results"
    with open("request.txt", "r", encoding="utf-8") as request_file:
        prompt = request_file.read()
    with open("models.json", "r", encoding="utf-8") as models_file:
        models = json.load(models_file)
    if args.model:
        if args.model not in models:
            raise SystemExit(f"Model key not found: {args.model}")
        models = {args.model: models[args.model]}
    progress = Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    )
    with progress:
        task_id = progress.add_task("Running models", total=len(models))
        for model_key, model_config in models.items():
            model_name = model_config["m"]
            use_reasoning = model_config.get("r", False)
            logger.info("Calling model %s (reasoning=%s)", model_key, use_reasoning)
            try:
                response = call_llm(prompt, model_name, use_reasoning)
            except KeyboardInterrupt:
                logger.warning("Interrupted model %s; continuing", model_key)
                progress.advance(task_id)
                continue
            if response is None:
                logger.error("Skipping %s due to LLM error", model_key)
            else:
                review_prompt = response.choices[0].message.content
                logger.info("Reviewing output for %s", model_key)
                review_response = call_review_llm(review_prompt)
                review_json = review_response.choices[0].message.content if review_response else None
                output_path = write_response(output_root_dir, model_key, response, review_json)
                logger.info("Stored result for %s at %s", model_key, output_path)

            progress.advance(task_id)
        progress.update(task_id, description="Completed")


if __name__ == "__main__":
    main()
