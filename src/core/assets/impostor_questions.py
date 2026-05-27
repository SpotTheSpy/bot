import json
from typing import Dict, List, Set

from src.core.enums.impostor_player_role import ImpostorPlayerRole

with open("src/core/assets/impostor_questions.json", "r", encoding="utf-8") as file:
    impostor_questions: Dict[str, Dict[ImpostorPlayerRole, List[str]]] = json.load(file)


def get_impostor_questions() -> Dict[str, Dict[ImpostorPlayerRole, Set[str]]]:
    return {
        bucket_key: {
            role: set(questions)
            for role, questions in bucket.items()
        }
        for bucket_key, bucket in impostor_questions.items()
    }
