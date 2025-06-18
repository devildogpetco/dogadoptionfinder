from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import json
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll restrict this later
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        prompt = f"""
        Find dog adoption centers near {request.location}. Return EXACTLY this JSON format with 10 results:
        {{
            "centers": [
                {{
                    "rank": 1,
                    "name": "Center Name",
                    "address": "Full address",
                    "phone": "Phone number",
                    "website": "Website URL",
                    "hours": "Mon-Fri 9-5",
                    "distance": "2 miles",
                    "notes": "Adoption fees start at $50"
                }}
            ]
        }}
        Only return valid JSON, no other text.
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        data = json.loads(text)
        
        return {
            "success": True,
            "data": data['centers']
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unable to find adoption centers. Please try again."
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
