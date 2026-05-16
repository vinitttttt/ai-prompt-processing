## Intucate Backend Case Study (ai-prompt-processing):
A FastAPI backend project that accepts education-related questions, builds prompts from MongoDB templates, calls an external AI API using OpenRouter, stores request/response history, and supports both single and batch processing.

## Tech Stack

- Python
- FastAPI
- MongoDB Atlas
- Motor
- httpx
- OpenRouter API
- Pydantic
- python-dotenv
- Uvicorn

## What This Project Does

This backend supports two main flows:

1. Single question flow

text
User question
→ Fetch prompt template from MongoDB
→ Replace {{userInput}}
→ Call OpenRouter AI API
→ Store request and response in history
→ Return AI response

## How To Run :
cd path
.\venv\Scripts\Activate.ps1
uvicorn App.main:app --reload
Uvicorn running on local host