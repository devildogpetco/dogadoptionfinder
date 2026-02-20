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

# Using the most stable 2026 connection
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a JSON object with a list called 'centers' containing name, address, phone, website, hours, distance, and notes."
        
        # We call the model directly by name
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # Clean up the response to ensure it's valid JSON
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        
        data = json.loads(result_text)
        return {"success": True, "data": data.get('centers', [])}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "System Online - Final Stable Build"}
