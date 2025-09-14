from typing import List, Tuple, Dict

def reduce_synonyms(tag_scores: List[Tuple[int, float]], tag_to_group: Dict[int, Tuple[int]]) -> List[Tuple[int, float]]:
    tag_map = dict(tag_scores)
    group_best = {}

    for tid, score in tag_map.items():
        if tid not in tag_to_group:
            continue
        group = tag_to_group[tid]
        current_best = group_best.get(group, (None, -1))
        if score > current_best[1]:
            group_best[group] = (tid, score)

    reduced = {tid: score for group, (tid, score) in group_best.items()}
    for tid, score in tag_map.items():
        if tid not in tag_to_group:
            reduced[tid] = score

    return sorted(reduced.items(), key=lambda x: x[1], reverse=True)