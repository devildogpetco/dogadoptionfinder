from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from google import genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Using the New Unified 2026 Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
STABLE_MODEL = "gemini-1.5-flash"

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a JSON object with a list called 'centers' containing name, address, phone, website, hours, distance, and notes."
        
        # This is the modern 2026 way to call the AI
        response = client.models.generate_content(
            model=STABLE_MODEL,
            contents=prompt
        )
        
        data = json.loads(response.text.strip())
        return {"success": True, "data": data.get('centers', [])}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Finder Active - 2026 Unified Standard"}
