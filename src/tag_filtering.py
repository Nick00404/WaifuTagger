from typing import List, Dict, Set, Tuple

def process_filtering(tag_scores: List[Tuple[int, float]], valid_tag_ids: Set[int], id_to_name: Dict[int, str], blacklist_tags: Set[str], max_tags: int) -> List[str]:
    final_tags = []
    for tid, _ in tag_scores:
        if tid not in valid_tag_ids:
            continue
        tag_name = id_to_name[tid]
        if tag_name in blacklist_tags:
            continue
        final_tags.append(tag_name)
        if len(final_tags) >= max_tags:
            break
    return final_tags

def apply_special_rules(tags: List[str]) -> List[str]:
    tags = list(tags)
    
    # Existing special rules
    if "no_humans" in tags and "solo" in tags:
        tags.remove("solo")
    if "head_out_of_frame" in tags and "solo" in tags:
        tags.remove("solo")
    
    # Color tag validation
    color_tags = [t for t in tags if t.startswith("color_")]
    added_skin = False
    for color in color_tags:
        parts = color.split('_', 1)
        if len(parts) < 2:
            continue  # Skip invalid color format
        base_color = parts[1]
        skin_tag = f"{base_color}_skin"
        if skin_tag in tags and "skin" not in tags:
            tags.append("skin")
            added_skin = True
            break  # Add only once
    
    # Special case handling for composite tags
    if "school_uniform" in tags:
        required = {"shirt", "skirt"}
        if not all(t in tags for t in required):
            pass  # Optionally handle warnings
    
    # Presence flag validation
    if "no_humans" in tags:
        human_indicators = {"smile", "open_mouth", "colored_tongue", "earrings", "jewelry"}
        if any(t in tags for t in human_indicators):
            pass  # Optionally handle exclusivity issues
    
    # Compound tag check
    if 'black_jacket' in tags:
        pass  # Optionally handle validation error
    
    # Hierarchy conflict check
    if 'school_uniform' in tags and 'skirt' in tags:
        pass  # Optionally handle validation error
    
    # Missing subcomponents check
    if 'school_uniform' in tags and not any(t in tags for t in ['blazer', 'ribbon', 'tie']):
        pass  # Optionally handle validation error
    
    # Entangled tags check
    if 'no_humans' in tags and any(t in tags for t in ['cleavage', 'profanity']):
        pass  # Optionally handle validation error
    
    return tags