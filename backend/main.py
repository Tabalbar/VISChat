from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env in production (Render)
# and from local .env if not already set (for local dev)
dotenv_path = "/etc/secrets/.env"
print("ENV found:", os.getenv("OPENAI_API_KEY"))
print("Does .env exist?", os.path.exists("/etc/secrets/.env"))

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # Fallback for local dev

# Access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

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
    # print(req.messages)
    # Convert Pydantic models to dicts for OpenAI client
    message_dicts = [msg.model_dump() for msg in req.messages]

    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=message_dicts,
    )
    print(completion.choices)
    # Replace this with chart/LLM logic
    return {
        "reply": f"{completion.choices[0].message.content}",
    }


@app.get("/")
def root():
    return {"status": "Server running"}
