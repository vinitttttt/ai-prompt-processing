def build_final_prompt(template: str, user_input: str) -> str:
    # Replace the placeholder in the DB prompt with the user's question.
    return template.replace("{{userInput}}", user_input)
