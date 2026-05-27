import json
from itertools import chain
from typing import Dict, List

from src.core.enums.imposter_player_role import ImposterPlayerRole


def main() -> None:
    with open("imposter_questions.json", "r", encoding="utf-8") as file:
        imposter_questions: Dict[str, Dict[ImposterPlayerRole, List[str]]] = json.load(file)

    flattened_imposter_questions = sorted(
        chain.from_iterable(
            chain.from_iterable(bucket.values() for bucket in imposter_questions.values())
        )
    )

    with open("imposter_questions.ftl", "w", encoding="utf-8") as file:
        file.write(
            "\n".join(
                [
                    f"imposter-question-{imposter_question} = ..."
                    for imposter_question in flattened_imposter_questions
                ]
            )
        )


if __name__ == '__main__':
    main()
