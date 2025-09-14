import os
import sys
import json
import yaml
import re
import gc
from tqdm import tqdm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from src.logger import setup_logger
from src.util import load_seen_paths, save_tagged_page, log_memory_usage
from src.tagger import Tagger

def natural_sort_key(s: str):
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

# Configuration setup
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.yaml")
tags_path = os.path.join(base_dir, "src", "selected_tags.csv")
blacklist_path = os.path.join(base_dir, "blacklist.txt")

# Load config
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

MODEL_ID = config["model"]["id"]
BASE_DIR = config["paths"]["base_dir"]
BATCH_SIZE = config["batch_processing"]["batch_size"]
OUTPUT_SUFFIX = config["paths"]["output_jsonl_suffix"]
FOLDERS_FOR_OUTPUT = config["folders_for_output"]

safe_model_id = MODEL_ID.replace("/", "_")
log_path = os.path.join(base_dir, "logs", f"{safe_model_id}.log")
logger = setup_logger(safe_model_id, log_file=log_path)

def prepare_output_path(folder: str) -> str:
    output_dir = os.path.join(base_dir, "outputs", folder)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{folder}_{OUTPUT_SUFFIX}")

def main():
    try:
        logger.info(f"Initializing tagger with model: {MODEL_ID}")
        tagger = Tagger(config_path, tags_path, blacklist_path)

        for folder in FOLDERS_FOR_OUTPUT:
            input_folder_path = os.path.join(BASE_DIR, folder)
            output_path = prepare_output_path(folder)
            seen_paths = load_seen_paths(output_path)

            with open(output_path, "a", encoding="utf-8") as out_file:
                subfolders = [
                    d for d in os.listdir(input_folder_path)
                    if os.path.isdir(os.path.join(input_folder_path, d))
                ]
                subfolders.sort(key=natural_sort_key)

                for subfolder in tqdm(subfolders, desc=f"Processing {folder}"):
                    subfolder_path = os.path.join(input_folder_path, subfolder)
                    image_files = [
                        fname for fname in os.listdir(subfolder_path)
                        if fname.lower().endswith((".png", ".jpg", ".jpeg"))
                    ]
                    image_files.sort(key=natural_sort_key)

                    batch_paths = []
                    for fname in image_files:
                        rel_path = os.path.join(folder, subfolder, fname).replace("\\", "/")
                        if rel_path not in seen_paths:
                            batch_paths.append(rel_path)

                    for i in tqdm(range(0, len(batch_paths), BATCH_SIZE),
                                  desc=f"  → {subfolder}", leave=False):
                        batch_chunk = batch_paths[i:i + BATCH_SIZE]

                        mem_before = log_memory_usage(f"Pre-batch {i // BATCH_SIZE}")
                        results = tagger.tag_images(batch_chunk, BASE_DIR)
                        logger.debug(f"Memory delta: {log_memory_usage('Post-batch') - mem_before:.2f} MB")

                        for result in results:
                            # Save the tags list properly
                            save_tagged_page(result["image_path"], result["tags"], output_path)

                        del results
                        gc.collect()

    except Exception as e:
        import traceback
        logger.critical(f"Fatal error: {str(e)}\n{traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main()
