import os
import yaml
import torch
import pandas as pd
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageClassification
from typing import List, Dict

from tag_synonyms import reduce_synonyms
from tag_filtering import process_filtering, apply_special_rules

class Tagger:
    def __init__(self, config_path: str, tags_csv_path: str, blacklist_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.model_id = self.config["model"]["id"]
        self.threshold = self.config["tagging"]["threshold"]
        self.max_tags = self.config["tagging"]["max_tags"]
        self.synonym_groups = self.config.get("synonym_groups_by_id", [])
        self.batch_size = self.config["batch_processing"]["batch_size"]
        self.use_cuda = self.config["device"]["use_cuda_if_available"] and torch.cuda.is_available()

        self.tags_df = pd.read_csv(tags_csv_path)
        self.id_to_name = dict(zip(self.tags_df["tag_id"], self.tags_df["name"]))
        self.valid_tag_ids = set(self.tags_df["tag_id"])

        with open(blacklist_path, "r") as f:
            self.blacklist_tags = set(line.strip() for line in f if line.strip())

        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForImageClassification.from_pretrained(self.model_id).to(self.device)
        self.model.eval()

        self.tag_to_group = {}
        for group in self.synonym_groups:
            for tid in group:
                self.tag_to_group[tid] = tuple(group)

    def process_batch(self, images: List[Image.Image]) -> List[List[float]]:
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return torch.sigmoid(outputs.logits).cpu().numpy()

    def tag_images(self, image_paths: List[str], base_dir: str) -> List[Dict]:
        results = []
        batch = []
        batch_paths = []

        for img_path in image_paths:
            full_path = os.path.join(base_dir, img_path)
            try:
                img = Image.open(full_path).convert("RGB")
                batch.append(img)
                batch_paths.append(img_path)
            except Exception as e:
                print(f"Skipping corrupt image {img_path}: {e}")
                continue

            if len(batch) == self.batch_size:
                results.extend(self._process_and_tag(batch, batch_paths))
                batch = []
                batch_paths = []

        if batch:
            results.extend(self._process_and_tag(batch, batch_paths))
        return results

    def _process_and_tag(self, batch_images: List[Image.Image], batch_paths: List[str]) -> List[Dict]:
        batch_results = []
        scores_batch = self.process_batch(batch_images)

        for rel_path, img_scores in zip(batch_paths, scores_batch):
            # Filter tags by threshold
            tag_scores = [
                (self.tags_df.iloc[i]["tag_id"], score)
                for i, score in enumerate(img_scores)
                if score > self.threshold
            ]
            # Sort descending by confidence
            tag_scores = sorted(tag_scores, key=lambda x: x[1], reverse=True)
            # Reduce synonyms
            tag_scores = reduce_synonyms(tag_scores, self.tag_to_group)
            # Filter and limit tags
            final_tags = process_filtering(
                tag_scores,
                self.valid_tag_ids,
                self.id_to_name,
                self.blacklist_tags,
                self.max_tags
            )
            # Apply any special rules
            final_tags = apply_special_rules(final_tags)

            batch_results.append({
                "image_path": rel_path,
                "tags": final_tags,  # KEEP tags as list of strings
                "caption": ""
            })

        return batch_results
