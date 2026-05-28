import json
from itertools import chain
from typing import Dict, List, Sequence


def main() -> None:
    with open("secret_words.json", "r", encoding="utf-8") as file:
        secret_words: Dict[str, List[str]] = json.load(file)

    flattened_secret_words: Sequence[str] = sorted(list(set(chain.from_iterable(secret_words.values()))))

    with open("secret_words.ftl", "w", encoding="utf-8") as file:
        file.write(
            "\n".join(
                [
                    f"secret-word-{secret_word} = {secret_word.replace('_', ' ').title()}"
                    for secret_word in flattened_secret_words
                ]
            )
        )


if __name__ == '__main__':
    main()
