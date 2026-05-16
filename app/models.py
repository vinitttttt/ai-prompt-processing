from pydantic import BaseModel

class PromptRequest(BaseModel):
    userInput: str