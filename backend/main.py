from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

OpenAI.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()
client = OpenAI()

# Allow CORS from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("HEllo Worldddd")

# Define the expected JSON structure


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.post("/chat")
async def chat_handler(req: ChatRequest):
    print(req)
    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=req.messages,
    )
    # Replace this with chart/LLM logic
    return {
        "reply": f"{completion.choices[0].message.content}",
    }


@app.get("/")
def root():
    return {"status": "Server running"}
