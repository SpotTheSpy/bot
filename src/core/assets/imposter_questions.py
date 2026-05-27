import json
from typing import Dict, List, Set

from src.core.enums.imposter_player_role import ImposterPlayerRole

with open("src/core/assets/imposter_questions.json", "r", encoding="utf-8") as file:
    imposter_questions: Dict[str, Dict[ImposterPlayerRole, List[str]]] = json.load(file)


def get_imposter_questions() -> Dict[str, Dict[ImposterPlayerRole, Set[str]]]:
    return {
        bucket_key: {
            role: set(questions)
            for role, questions in bucket.items()
        }
        for bucket_key, bucket in imposter_questions.items()
    }
