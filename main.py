from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import google.generativeai as genai

app = FastAPI()

# Allow your Shopify site to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Connect to the stable AI endpoint
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"Find 10 real dog adoption centers near {request.location}. Return ONLY a JSON object with a list called 'centers' containing name, address, phone, website, hours, distance, and notes."
        
        # Use the stable content generation method
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        # Parse and return the results
        data = json.loads(response.text.strip())
        return {"success": True, "data": data.get('centers', [])}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Dog Finder System Online - Stable v10"}
