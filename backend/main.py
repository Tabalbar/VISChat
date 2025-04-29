from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow CORS from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.post("/chat")
async def chat_handler(query: Query):
    # Replace this with chart/LLM logic
    return {
        "reply": f"You said: {query.message}"
    }

@app.get("/")
def root():
    return {"status": "Server running"}
