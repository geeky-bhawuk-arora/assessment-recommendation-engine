import requests
from bs4 import BeautifulSoup
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# --- 1. Define Structured Output Schema using Pydantic ---
class AssessmentDetails(BaseModel):
    """Schema for extracting structured details from assessment descriptions."""
    adaptive_support: str = Field(description="Either 'Yes' or 'No'. Infer from context.")
    duration: int = Field(description="Duration of the assessment in minutes. Infer a sensible duration (e.g., 30) if not explicitly mentioned.")
    remote_support: str = Field(description="Either 'Yes' or 'No'. Assume 'Yes' unless stated otherwise.")
    test_type: list[str] = Field(description="Categories or types (e.g., Cognitive, Personality, Judgment, Leadership).")
    
# --- 2. Initialize Gemini Client ---
try:
    # Client automatically picks up the GEMINI_API_KEY environment variable
    client = genai.Client() 
except Exception as e:
    print(f"Warning: Gemini Client failed to initialize. Error: {e}")
    client = None

# --- 3. Function to Extract Details using Gemini ---
def enrich_assessment_data(name, description):
    """Uses the Gemini API to extract structured fields from a description."""
    if not client:
        return {
            "adaptive_support": "N/A (Gemini not initialized)",
            "duration": 0,
            "remote_support": "N/A (Gemini not initialized)",
            "test_type": ["N/A"]
        }

    prompt = f"Assessment Name: {name}. Description: {description}. Extract the following structured details based on the assessment name and description. If information is missing, use your general knowledge about such assessments."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AssessmentDetails,
            ),
        )
        # The response.text is a JSON string conforming to the Pydantic schema
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error calling Gemini for {name}: {e}")
        return {
            "adaptive_support": "Error",
            "duration": 0,
            "remote_support": "Error",
            "test_type": ["Error"]
        }

BASE_URL = "https://www.shl.com/products/product-catalog/"

def scrape_shl_catalog():
    resp = requests.get(BASE_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')

    assessments = []
    cards = soup.select('a.c-product-card')

    for card in cards:
        name = card.text.strip()
        url = card['href']
        if "pre-packaged" in url.lower():
            continue

        try:
            page = requests.get(url)
            inner = BeautifulSoup(page.text, 'html.parser')
            desc = inner.select_one('div.c-product-hero__summary')
            desc_text = desc.text.strip() if desc else ""
        except:
            desc_text = ""
        
        # --- NEW STEP: Call Gemini to enrich the data ---
        enriched_details = enrich_assessment_data(name, desc_text)
        # ------------------------------------------------

        assessments.append({
            "name": name,
            "url": url,
            "description": desc_text,
            "adaptive_support": enriched_details["adaptive_support"],
            "duration": enriched_details["duration"],
            "remote_support": enriched_details["remote_support"],
            "test_type": enriched_details["test_type"]
        })

    with open("data/assessments.json", "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted and Enriched {len(assessments)} assessments")

if __name__ == "__main__":
    scrape_shl_catalog()