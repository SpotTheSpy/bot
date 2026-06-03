import json
from typing import List, Literal, Dict

from openai import OpenAI, BaseModel
from pydantic import ConfigDict

from config import config

_MODEL = "gpt-5"


def get_prompt(name: str) -> str:
    with open(f"scripts/generate_questions/prompts/{name.upper()}.txt", "r") as file:
        prompt: str = file.read()

    return prompt


class ModelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Message(ModelResponse):
    role: Literal["user", "assistant"]
    content: str


class AssistantMessage(Message):
    role: Literal["assistant"] = "assistant"
    content: str


def conversation_to_string(conversation: List[Message]) -> List[Dict[str, str]]:
    return [message.model_dump(mode="json") for message in conversation]


def main() -> None:
    api_key: str = config.openai_key.get_secret_value() if config.openai_key else input("Enter your OpenAI API key: ").strip()
    client: OpenAI = OpenAI(api_key=api_key)

    system_prompt: str = get_prompt("system")

    while True:
        conversation: List[Message] = [
            Message(role="user", content=get_prompt("workflow")),
            AssistantMessage(content="Understood."),
            Message(role="user", content=get_prompt("question_specifics")),
            AssistantMessage(content="Understood."),
        ]

        with open("scripts/generate_questions/used_topics.json", "r") as file:
            used_topics: List[Dict[str, str]] = json.load(file)

        questions: Dict[str, Dict[str, str]] = {}
        selected_question_index: int = 0
        while True:
            used_topics_string = "\n".join([
                f"{index + 1}. Key: {used_topic['key']}, Topic: {used_topic['topic']}"
                for index, used_topic in enumerate(used_topics)
            ]) if used_topics else "No topics were used for now..."

            print("Generating questions...\n")
            response: AssistantMessage = client.responses.parse(
                model=_MODEL,
                input=conversation_to_string(
                    [
                        *conversation,
                        Message(role="user", content=get_prompt("question_list").replace("%%", used_topics_string)),
                    ]
                ),
                instructions=system_prompt,
                text_format=AssistantMessage,
            ).output_parsed

            try:
                questions: Dict[str, Dict[str, str]] = json.loads(response.content)

                question_list_string: str = '\n'.join([
                    f"{index + 1}. {question['topic']}\nCITIZEN: {question['citizen']}\nIMPOSTOR: {question['impostor']}"
                    for index, (bucket_key, question) in enumerate(questions.items())
                ])
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                continue

            print(f"Generated questions:\n\n{question_list_string}\n")
            selected_question_index: int = int(input("Please select a question index (0 for re-generating): "))

            if selected_question_index:
                break

        conversation.append(response)
        bucket_key, question = list(questions.items())[selected_question_index - 1]

        used_topics.append({"key": bucket_key, "topic": question["topic"]})

        bucket: Dict[str, Dict[str, str]] = {}
        bucket_string: str = ""
        while True:
            print("Generating bucket...\n")
            response: AssistantMessage = client.responses.parse(
                model=_MODEL,
                input=conversation_to_string(
                    [
                        *conversation,
                        Message(role="user", content=get_prompt("question_bucket").replace(
                            "%%",
                            json.dumps({bucket_key: question}, indent=4)
                        )),
                    ]
                ),
                instructions=system_prompt,
                text_format=AssistantMessage,
            ).output_parsed

            try:
                bucket: Dict[str, Dict[str, str]] = json.loads(response.content)

                citizen_bucket_string: str = '\n'.join([
                    f"{index + 1}. ({key}) ({question})"
                    for index, (key, question) in enumerate(bucket["citizen"].items())
                ])
                impostor_bucket_string: str = '\n'.join([
                    f"{index + 1}. ({key}) ({question})"
                    for index, (key, question) in enumerate(bucket["impostor"].items())
                ])

                bucket_string: str = f"CITIZEN:\n{citizen_bucket_string}\n\nIMPOSTOR:\n{impostor_bucket_string}"
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                continue

            break

        print(f"Generated bucket:\n\n{bucket_string}\n")
        selected_questions: str = input("Please select questions which you want to save (1,2,3-4,5,6): ")

        citizen_questions: List[int] = list(map(lambda x: int(x) - 1, selected_questions.split("-")[0].split(",")))
        impostor_questions: List[int] = list(map(lambda x: int(x) - 1, selected_questions.split("-")[1].split(",")))

        bucket: Dict[str, Dict[str, str]] = {
            "citizen": {
                key: question
                for index, (key, question) in enumerate(bucket["citizen"].items())
                if index in citizen_questions
            },
            "impostor": {
                key: question
                for index, (key, question) in enumerate(bucket["impostor"].items())
                if index in impostor_questions
            }
        }

        with open("scripts/generate_questions/used_topics.json", "w") as file:
            json.dump(used_topics, file, indent=4)

        with open("scripts/generate_questions/questions.json", "r") as file:
            all_questions: Dict[str, Dict[str, Dict[str, str]]] = json.load(file)

        all_questions.update({bucket_key: bucket})

        with open("scripts/generate_questions/questions.json", "w") as file:
            json.dump(all_questions, file, indent=4)

        should_continue: str = input("Saved. Continue? (y/n): ")

        if should_continue.strip().lower() != "y":
            break


if __name__ == '__main__':
    main()
