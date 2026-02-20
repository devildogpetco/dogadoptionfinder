from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Initialize Gemini client
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

model = "gemini-2.0-flash" 

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a JSON object with centers containing name, address, phone, website, hours, distance, and notes."
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        data = json.loads(response.text.strip())
        
        if 'centers' in data:
            return {"success": True, "data": data['centers']}
        return {"success": False, "error": "No centers found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "DDPC Dog Adoption Finder Agent is running"}
