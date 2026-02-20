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

# This is the "Magic Fix": It forces the connection to 'v1' (Stable) 
# instead of 'v1beta' (Experimental)
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(api_version='v1')
)

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a JSON object with a list called 'centers' containing name, address, phone, website, hours, distance, and notes."
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        # Clean the text in case the AI adds formatting
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        
        data = json.loads(result_text)
        return {"success": True, "data": data.get('centers', [])}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Dog Finder - Stable v1 Connection Online"}
