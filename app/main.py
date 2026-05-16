from fastapi import FastAPI, HTTPException

from .database import database
from .models import PromptRequest
from .utils import build_final_prompt


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Running"}


@app.get("/db-test")
async def test_database_connection():
    await database.command("ping")
    return {"message": "MongoDB connection successful"}


@app.post("/seed-prompt")
async def seed_prompt():
    prompt_document = {
        "_id": "Education_Prompt",
        "template": "You are an expert in education domain. Answer the following: {{userInput}}",
    }

    await database.prompts.update_one(
        {"_id": prompt_document["_id"]},
        {"$set": prompt_document},
        upsert=True,
    )

    return {"message": "Prompt saved successfully"}


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

    final_prompt = build_final_prompt(
        template=prompt["template"],
        user_input=request.userInput,
    )

    return {
        "response": final_prompt
    }