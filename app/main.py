import asyncio
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException

from .ai_service import call_openrouter
from .database import database
from .utils import build_final_prompt
from .models import BatchPromptRequest, PromptRequest, TokenResponse, UserLoginRequest, UserRegisterRequest
from .auth import create_access_token, get_current_user, hash_password, verify_password

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

    await database.history.insert_one(history_document) #save history to mongidb

    return ai_response #return answer


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


@app.post("/register")
async def register_user(request: UserRegisterRequest):
    email = request.email.strip().lower()

    # Check if this email is already registered
    existing_user = await database.users.find_one({"email": email})

    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Never store plain passwords in the database
    hashed_password = hash_password(request.password)

    user_document = {
        "email": email,
        "hashedPassword": hashed_password,
        "createdAt": datetime.now(timezone.utc),
    }

    await database.users.insert_one(user_document)

    return {"message": "User registered successfully"}


@app.post("/login", response_model=TokenResponse)
async def login_user(request: UserLoginRequest):
    email = request.email.strip().lower()

    # Find user by email
    user = await database.users.find_one({"email": email})

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Compare plain password with stored hashed password
    password_is_valid = verify_password(
        plain_password=request.password,
        hashed_password=user["hashedPassword"],
    )

    if not password_is_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Store user identity inside token
    access_token = create_access_token(
        data={"sub": user["email"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    # Returns the logged-in user from the JWT token
    return {
        "email": current_user["email"]
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

    tasks = [                             #asyncio.gather
        process_single_question(       #final prompt 
            user_input=user_input,
            template=prompt["template"],
        )
        for user_input in request.userInputs
    ]

    ai_responses = await asyncio.gather(*tasks)

    return {
        "responses": ai_responses
    }
