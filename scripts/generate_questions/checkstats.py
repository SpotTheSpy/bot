import json

with open("questions.json", "r") as f:
    questions = json.load(f)

print(len(questions))
