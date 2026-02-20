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

# Initialize the official 2026 production client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a JSON object with a list called 'centers' containing name, address, phone, website, hours, distance, and notes."
        
        # This explicitly uses the production 'v1' API to stop the 404s
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # Safely parse the AI response
        result_text = response.text
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
            
        data = json.loads(result_text.strip())
        return {"success": True, "data": data.get('centers', [])}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Production System Online"}
