import os
import json
import psutil
from typing import Set, List

def save_tagged_page(image_path: str, tags: List[str], output_jsonl_path: str):
    record = {
        "image_path": image_path,
        "tags": tags,
        "caption": ""
    }
    with open(output_jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_seen_paths(jsonl_path: str) -> Set[str]:
    seen = set()
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    seen.add(data["image_path"])
                except json.JSONDecodeError:
                    continue
    return seen

def log_memory_usage(stage: str) -> float:
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 ** 2
    return mem_mb