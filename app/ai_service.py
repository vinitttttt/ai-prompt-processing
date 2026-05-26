
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException


load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


# Sends a prompt to OpenRouter AI and returns the text response
async def call_openrouter(final_prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("OPENROUTER_MODEL")


    if not api_key:
        raise HTTPException( 
            status_code=500,
            detail="OPENROUTER_API_KEY is missing in .env",
        ) #if key is missing, raise this error code

    if not model_name:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_MODEL is missing in .env",
        ) #if model name missing then raise error

 
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    } #create request headers

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": final_prompt,
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client: # Send POST request,  timeout after 30s
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
            )

            response.raise_for_status() #raise error for failed responses

    except httpx.HTTPStatusError as error: 
        raise HTTPException(
            status_code=error.response.status_code,
            detail=f"OpenRouter API error: {error.response.text}",
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="Could not connect to OpenRouter API",
        ) #handel open router error when theres no network or connec failure

    response_data = response.json() 
    return response_data["choices"][0]["message"]["content"]
