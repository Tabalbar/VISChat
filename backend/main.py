from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from csv_llm import LLM
import requests
import json
from datetime import datetime
import pandas as pd
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
llm = LLM(client, {"model": "gpt-4.1", "temperature": 0.0})
token = "71c5efcd8cfe303f2795e51f01d19c6"

# Allow CORS from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    user_prompt = message_dicts[-1]["content"]

    # GET STATIONS
    stations = requests.get("https://api.hcdp.ikewai.org/mesonet/db/stations",
                            headers={"Authorization": f"Bearer {token}"})
    stations_extracted, station_reasoning = llm.prompt_select_stations(
        user_prompt, stations.text)
    print(stations_extracted)

    # CREATE ALL_ATTRIBUTES SET WITH UNIQUE VARIABLES
    all_attributes = set()
    for station in stations_extracted:
        # Query the API for a single data point to get all variables
        res = requests.get(
            f"https://api.hcdp.ikewai.org/mesonet/db/measurements",
            params={
                "station_ids": station,
                "limit": 100,
                "row_mode": "json",
                "join_metadata": "true"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        if res.status_code == 200:
            data = res.json()
            if data and len(data) > 0:
                # Extract just the variable name from each measurement
                variables = [item.get('variable', '') for item in data]
                # Add unique variables to the set

                all_attributes.update(variables)

    # EXTRACT ATTRIBUTES FRMO QUERY BASED ON ALL_ATTRIBUTES
    attributes_extracted, attribute_reasoning = llm.prompt_select_attributes(
        user_prompt, list(all_attributes))
    print(attributes_extracted)

    # EXTRACT CHART TYPE FROM QUERY
    chart_type_extracted, _ = llm.prompt_charts_via_chart_info(
        user_prompt, attributes_extracted)
    print(chart_type_extracted)

    time_now = datetime.utcnow().isoformat() + "Z"
    print(time_now, 'timeNOW')
    # EXTRACT START AND END DATE FROM QUERY
    date, date_reasoning = llm.prompt_select_dates(
        user_prompt, time_now)
    # SCHEMA {"start_date": str, "end_date": str}
    start_date = date["start_date"]
    end_date = date["end_date"]
    print(start_date, end_date)

    # ANSWER THE QUERY
    url = f"https://api.hcdp.ikewai.org/mesonet/db/measurements?station_ids={','.join(stations_extracted)}&var_ids={','.join(attributes_extracted)}&start_date={start_date}&end_date={end_date}&row_mode=json&join_metadata=true"
    res = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    # Validate JSON response
    try:
        data = json.loads(res.text)
        df = pd.DataFrame(data)
    except json.JSONDecodeError:
        print("Invalid JSON response from API")
        return {"error": "Invalid JSON response from API"}

    # Check for empty data
    if df.empty:
        print("No data retrieved from API")
        return {"error": "No data retrieved from API"}

    # Ensure required columns exist
    required_columns = {"timestamp", "value", "variable", "station_name"}
    if not required_columns.issubset(df.columns):
        print("Missing required columns:", required_columns - set(df.columns))
        return {"error": f"Missing required columns: {required_columns - set(df.columns)}"}

    # Convert timestamp to datetime and handle errors
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors="coerce")
    df = df.dropna(subset=["timestamp"])  # Drop rows where timestamp is NaT

    # Convert value to numeric and remove NaN
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])  # Drop rows where value is NaN

    # Convert timestamps to hourly intervals
    df["timestamp"] = df["timestamp"].dt.floor("H")

    # Aggregate data: mean per timestamp-variable-station_name
    df_resampled = df.groupby(["timestamp", "variable", "station_name"]).agg(
        {"value": "mean"}).reset_index()

    # Convert DataFrame to JSON format
    measurements_json = df_resampled.to_dict(orient="records")

    # Generate summary
    summary, _ = llm.prompt_summarize_reasoning(
        user_prompt, attribute_reasoning, station_reasoning, measurements_json
    )

    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=message_dicts,
    )

    # Replace this with chart/LLM logic
    return {
        "reply": f"{summary}",
        "data": measurements_json,
    }


@app.get("/")
def root():
    return {"status": "Server running"}
