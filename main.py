from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import List, Optional
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
    api_key="AIzaSyA1sXV36RyvgKxooP1HIsb-OQU4htxVnnw"  # Hardcoded for now
)

model = "gemini-2.0-flash-exp"  # Using stable model without thinking

class LocationRequest(BaseModel):
    location: str

@app.post("/api/find-adoption-centers")
async def find_adoption_centers(request: LocationRequest):
    try:
        # Simple prompt for JSON only
        prompt = f"""Find dog adoption centers near {request.location}. 

Return ONLY a JSON object in this exact format with 10 real adoption centers:
{{
    "centers": [
        {{
            "rank": 1,
            "name": "Actual Center Name",
            "address": "Full street address",
            "phone": "(xxx) xxx-xxxx",
            "website": "https://website.com",
            "hours": "Mon-Fri 9AM-5PM",
            "distance": "X miles",
            "notes": "Adoption fees, special requirements, etc"
        }}
    ]
}}

Important: Return ONLY the JSON object, no other text or markdown."""
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # Lower temperature for more consistent formatting
                response_mime_type="application/json"  # Request JSON response
            )
        )
        
        # Get the text response
        text = response.text.strip()
        
        # Parse JSON directly
        try:
            # First try direct parsing
            data = json.loads(text)
        except:
            # If that fails, try to extract JSON from markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Try parsing again
            data = json.loads(text)
        
        # Validate we have centers
        if 'centers' in data and len(data['centers']) > 0:
            return {
                "success": True,
                "data": data['centers']
            }
        else:
            return {
                "success": False,
                "error": "No adoption centers found in response"
            }
            
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {str(e)}")
        return {
            "success": False,
            "error": "Invalid response format from AI"
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "success": False,
            "error": "Unable to find adoption centers. Please try again."
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "DDPC Dog Adoption Finder Agent is running"}
