
from pydantic import BaseModel, Field, field_validator


# Request for a single question
class PromptRequest(BaseModel):
    userInput: str = Field(..., min_length=1)  # Must have at least 1 character

    @field_validator("userInput")   #runs validation for user input 
    @classmethod
    def user_input_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("userInput must not be blank")

        return value


# Request model for multiple questions at once
class BatchPromptRequest(BaseModel):
    userInputs: list[str] = Field(..., min_length=1)  # List must have at least 1 item

    @field_validator("userInputs")
    @classmethod
    def user_inputs_must_not_contain_blank_values(cls, values: list[str]) -> list[str]:  #custom valid
        for value in values:
            if not value.strip(): #remove spaces
                raise ValueError("userInputs must not contain blank values")

        return values

#jwt auth
class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str