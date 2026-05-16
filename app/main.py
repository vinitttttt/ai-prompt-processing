import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from .ai_service import call_openrouter
from .database import database
from .models import BatchPromptRequest, PromptRequest
from .utils import build_final_prompt


app = FastAPI()


async def process_single_question(user_input: str, template: str) -> str:

    final_prompt = build_final_prompt(
        template=template,
        user_input=user_input,
    )

    # Send prompt to AI and get response
    ai_response = await call_openrouter(final_prompt)

    # Save the full exchange to history
    history_document = {
        "userInput": user_input,
        "finalPrompt": final_prompt,
        "response": ai_response,
        "createdAt": datetime.now(timezone.utc),
    }

    await database.history.insert_one(history_document)

    return ai_response


# confirms the server is running
@app.get("/")
async def root():
    return {"message": "Running"}


# Pings MongoDB to confirm the DB connection works
@app.get("/db-test")
async def test_database_connection():
    await database.command("ping")
    return {"message": "MongoDB connection successful"}


# Inserts the default education prompt in DB
@app.post("/seed-prompt")
async def seed_prompt():
    prompt_document = {
        "_id": "Education_Prompt",
        "template": "You are an expert in education domain. Answer the following: {{userInput}}",
    }

    #update if exists, insert if not
    await database.prompts.update_one(
        {"_id": prompt_document["_id"]},
        {"$set": prompt_document},
        upsert=True,
    )

    return {"message": "Prompt saved successfully"}


# Fetches the education prompt and returns 
@app.get("/prompt-test")
async def test_prompt_fetch():
    prompt = await database.prompts.find_one({"_id": "Education_Prompt"})

    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return {
        "id": prompt["_id"],
        "template": prompt["template"],
    }


@app.post("/ask")
async def ask_question(request: PromptRequest):
    prompt = await database.prompts.find_one({"_id": "Education_Prompt"})

    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    ai_response = await process_single_question(
        user_input=request.userInput,
        template=prompt["template"],
    )

    return {
        "response": ai_response
    }


@app.post("/ask-batch")
async def ask_batch_questions(request: BatchPromptRequest):
    prompt = await database.prompts.find_one({"_id": "Education_Prompt"})

    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    tasks = [
        process_single_question(
            user_input=user_input,
            template=prompt["template"],
        )
        for user_input in request.userInputs
    ]

    ai_responses = await asyncio.gather(*tasks)

    return {
        "responses": ai_responses
    }