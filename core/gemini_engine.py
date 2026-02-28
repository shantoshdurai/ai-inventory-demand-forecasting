import google.generativeai as genai
import json
from PIL import Image

from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def parse_text_input(user_text):
    """
    Parses a user input text describing sales or restocks.
    Expected to return a JSON list of dictionaries with keys:
    item, qty, type (sale/restock), date
    """
    if not GEMINI_API_KEY:
        return [{"error": "GEMINI_API_KEY is not configured in config."}]
        
    prompt = f"""
    You are an AI assistant for a small business.
    The user is inputting a log of sales or restocks.
    Parse the following text and output ONLY valid JSON format.
    The output should be a list of objects. Each object must have:
    - "item": Name of the product (string)
    - "qty": Quantity (number)
    - "type": "sale" or "restock" (string)
    - "date": Date in YYYY-MM-DD format, assuming today is the date if not mentioned (leave missing or null if unsure).

    Text: "{user_text}"
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        return [{"error": str(e)}]

def parse_image_input(image_file):
    """
    Parses a receipt or shelf photo using Gemini Vision.
    """
    if not GEMINI_API_KEY:
        return [{"error": "GEMINI_API_KEY is not configured in config."}]
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        img = Image.open(image_file)
        
        prompt = '''
        You are an AI assistant for a small business.
        The user uploaded a photo of a receipt, handwritten log, or a shelf count.
        Extract the items and their quantities.
        Output ONLY valid JSON in this format (list of objects):
        [
          {"item": "ProductName", "qty": 5, "type": "restock"}
        ]
        Assume "type" is "restock" if it's a purchase receipt (e.g. from distributor), "sale" if it's a sales receipt, or "initial" if it's a shelf count. Date is today if not specified (leave missing or null if unsure).
        '''
        
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        return [{"error": str(e)}]
