from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    userInput: str = Field(..., min_length=1)

    @field_validator("userInput")
    @classmethod
    def user_input_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("userInput must not be blank")

        return value


class BatchPromptRequest(BaseModel):
    userInputs: list[str] = Field(..., min_length=1)

    @field_validator("userInputs")
    @classmethod
    def user_inputs_must_not_contain_blank_values(cls, values: list[str]) -> list[str]:
        for value in values:
            if not value.strip():
                raise ValueError("userInputs must not contain blank values")

        return values