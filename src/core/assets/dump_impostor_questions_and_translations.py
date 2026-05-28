import json
from typing import Dict, List

from src.core.enums.impostor_player_role import ImpostorPlayerRole


def main() -> None:
    with open("impostor_questions_and_translations.json", "r", encoding="utf-8") as file:
        data: Dict[str, Dict[ImpostorPlayerRole, Dict[str, str]]] = json.load(file)

    keys: Dict[str, Dict[ImpostorPlayerRole, List[str]]] = {}
    translations: Dict[str, str] = {}

    for bucket_key, bucket in data.items():
        new_bucket_keys: Dict[ImpostorPlayerRole, List[str]] = {}

        for role, i in bucket.items():
            new_bucket_keys[role] = list(i.keys())

            for k, v in i.items():
                translations[f"impostor-question-{k}"] = v

        keys[bucket_key] = new_bucket_keys

    with open("impostor_questions.json", "w", encoding="utf-8") as file:
        json.dump(keys, file, indent=2)

    with open("../../../locales/en/impostor_questions.ftl", "w", encoding="utf-8") as file:
        file.write(
            "\n".join(
                f"{k} = {v}"
                for k, v in translations.items()
            )
        )


if __name__ == '__main__':
    main()
