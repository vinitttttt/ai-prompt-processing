def build_final_prompt(template: str, user_input: str) -> str:
    return template.replace("{{userInput}}", user_input)
