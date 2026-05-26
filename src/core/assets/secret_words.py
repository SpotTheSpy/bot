import json
from typing import Any, Dict, Set

from src.core.enums.spy_category import SpyCategory

with open("src/core/assets/secret_words.json", "r", encoding="utf-8") as file:
    secret_words: Dict[str, Any] = json.load(file)


def get_secret_words(
        category: SpyCategory,
) -> Set[str]:
    return set(secret_words.get(category, list()))
