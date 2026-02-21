from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import re
from google import genai

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

class LocationRequest(BaseModel):
    location: str

def clean_json(text):
    text = text.strip()
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    text = re.sub(r'}\s*{', '},{', text)
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)
    return text

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a valid JSON object with a list called 'centers'. Each center must have: name, address, phone, website, hours, distance, and notes. Double-check that your JSON is valid before responding."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            }
        )

        raw_text = response.text.strip()

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            cleaned = clean_json(raw_text)
            data = json.loads(cleaned)

        return {"success": True, "data": data.get('centers', [])}

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "System Online"}
