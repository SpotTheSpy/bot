import json
from itertools import chain
from typing import Dict, List

from src.core.enums.impostor_player_role import ImpostorPlayerRole


def main() -> None:
    with open("impostor_questions.json", "r", encoding="utf-8") as file:
        impostor_questions: Dict[str, Dict[ImpostorPlayerRole, List[str]]] = json.load(file)

    flattened_impostor_questions = sorted(
        chain.from_iterable(
            chain.from_iterable(bucket.values() for bucket in impostor_questions.values())
        )
    )

    with open("impostor_questions.ftl", "w", encoding="utf-8") as file:
        file.write(
            "\n".join(
                [
                    f"impostor-question-{impostor_question} = ..."
                    for impostor_question in flattened_impostor_questions
                ]
            )
        )


if __name__ == '__main__':
    main()
