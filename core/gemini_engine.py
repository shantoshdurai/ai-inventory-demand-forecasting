import json
from datetime import date
from PIL import Image

from config import GEMINI_API_KEY, GEMINI_MODEL

_client = None


def _get_client():
    global _client
    if _client is None and GEMINI_API_KEY:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _call_gemma(prompt, image=None):
    """Call Gemma 4 31B with text and optional image."""
    client = _get_client()
    if client is None:
        return None, "API key not configured. Running in demo mode."
    try:
        contents = []
        if image is not None:
            contents.append(image)
        contents.append(prompt)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        )
        return response.text.strip(), None
    except Exception as e:
        return None, str(e)


def _extract_json(text):
    """Extract JSON from model response, handling markdown code blocks."""
    if "```json" in text:
        text = text.split("```json")[1]
    if "```" in text:
        text = text.split("```")[0]
    return json.loads(text.strip())


def parse_text_input(user_text):
    """Parse natural language transaction input using Gemma 4."""
    today = date.today().isoformat()
    prompt = f"""You are an AI assistant for a Kirana shop (Indian grocery/general store) inventory system.
Parse the following text describing sales or restocks into structured data.
Output ONLY valid JSON — a list of objects with these keys:
- "item": Product name (string)
- "qty": Quantity (number)
- "type": "sale" or "restock" (string)
- "date": Date in YYYY-MM-DD format. Today is {today}. Use today if not mentioned, null if unsure.

Common Kirana items: Toor Dal, Rice, Atta, Sugar, Tea, Oil, Maggi, Biscuits, Soap, Detergent, Milk, Bread, Eggs, etc.
Understand Hindi/English mixed input like "5 packet Maggi becha" (sold 5 Maggi), "20 kg Atta aaya" (restocked 20kg Atta).

Text: "{user_text}"
"""
    text, err = _call_gemma(prompt)
    if err:
        return [{"error": err}]
    try:
        return _extract_json(text)
    except Exception as e:
        return [{"error": f"Could not parse AI response: {e}"}]


def parse_image_input(image_file):
    """Parse receipt/invoice photo using Gemma 4 vision."""
    try:
        img = Image.open(image_file)
    except Exception as e:
        return [{"error": f"Could not open image: {e}"}]

    today = date.today().isoformat()
    prompt = f"""You are an AI assistant for a Kirana shop (Indian grocery store) inventory system.
The user uploaded a photo — it could be a receipt, bill, handwritten stock register, or shelf photo.
Extract all items and quantities you can see.
Output ONLY valid JSON as a list of objects:
[{{"item": "ProductName", "qty": 5, "type": "restock", "date": "{today}"}}]

Rules:
- "type" = "restock" for purchase bills/distributor receipts, "sale" for sales receipts, "initial" for shelf counts
- Use today's date ({today}) if not visible in the image
- Recognize Indian products, brands, and Hindi text
- Include price if visible as "price" field"""

    text, err = _call_gemma(prompt, image=img)
    if err:
        return [{"error": err}]
    try:
        return _extract_json(text)
    except Exception as e:
        return [{"error": f"Could not parse AI response: {e}"}]


def parse_voice_input(transcribed_text):
    """Parse voice-transcribed text — handles casual spoken language."""
    today = date.today().isoformat()
    prompt = f"""You are an AI assistant for a Kirana shop (Indian grocery/general store).
The following text was transcribed from voice input, so it may have:
- Casual spoken language, filler words
- Hindi-English mix (Hinglish)
- Approximate pronunciations

Parse it into inventory transactions.
Output ONLY valid JSON — a list of objects:
- "item": Product name (corrected spelling)
- "qty": Quantity (number)
- "type": "sale" or "restock"
- "date": "{today}"

Examples of voice input patterns:
- "aaj 10 kilo chawal becha aur 5 packet Maggi bhi" → 10 Rice sold, 5 Maggi sold
- "distributor se 50 kilo atta aaya hai aur 20 liter tel" → 50 Atta restocked, 20 Oil restocked
- "sold 3 dozen eggs and 10 bread packets" → 36 Eggs sold, 10 Bread sold

Voice text: "{transcribed_text}"
"""
    text, err = _call_gemma(prompt)
    if err:
        return [{"error": err}]
    try:
        return _extract_json(text)
    except Exception as e:
        return [{"error": f"Could not parse AI response: {e}"}]


def chat_with_advisor(user_message, inventory_context, chat_history=None):
    """AI advisor for Kirana shop business performance and inventory strategy."""
    system_prompt = f"""You are StockSense AI — an expert business advisor for Kirana shops (Indian grocery/general stores).
You speak in a friendly, practical tone. You can understand Hindi/English mixed questions.

You have access to the shop's real-time inventory data below. Use it to give specific,
actionable advice with exact product names and numbers.

CURRENT INVENTORY DATA:
{inventory_context}

YOUR EXPERTISE:
- Inventory management and restocking strategies
- Identifying fast-moving vs slow-moving products
- Seasonal demand patterns for Indian markets (festivals, monsoon, summer, winter)
- Pricing and margin optimization for Kirana shops
- Stockout risk analysis with days-remaining estimates
- Supplier order planning and cash flow management
- Product bundling and cross-selling suggestions

RESPONSE GUIDELINES:
- Be concise and actionable (under 300 words unless detailed analysis requested)
- Use specific numbers from the inventory data
- Suggest practical steps the shop owner can take TODAY
- Use markdown formatting for readability (tables, bold, bullet points)
- If asked in Hindi/Hinglish, respond in the same style
- End with a follow-up question to keep the conversation useful
"""

    history_text = ""
    if chat_history:
        for msg in chat_history[-10:]:
            role = "Shop Owner" if msg["role"] == "user" else "StockSense AI"
            history_text += f"\n{role}: {msg['content']}\n"

    full_prompt = system_prompt
    if history_text:
        full_prompt += f"\nCONVERSATION HISTORY:{history_text}"
    full_prompt += f"\nShop Owner: {user_message}\nStockSense AI:"

    text, err = _call_gemma(full_prompt)
    if err:
        return f"Sorry, I encountered an error: {err}"
    return text


def generate_ai_insights(inventory_context):
    """Generate AI-powered business insights for the dashboard."""
    prompt = f"""You are StockSense AI analyzing a Kirana shop's inventory.
Based on the data below, generate exactly 3 high-priority insights.

INVENTORY DATA:
{inventory_context}

Return ONLY valid JSON — a list of 3 objects:
- "title": Short headline (under 8 words)
- "detail": One sentence of actionable advice with specific numbers
- "severity": "critical", "warning", or "info"
- "metric": Key number (e.g. "3 days", "-23%", "142 units")

Focus on: stockout risks, trending demand, reorder timing, overstock issues, seasonal patterns."""

    text, err = _call_gemma(prompt)
    if err:
        return None
    try:
        return _extract_json(text)
    except Exception:
        return None


def analyze_performance(inventory_context):
    """Deep performance analysis for voice conversation."""
    prompt = f"""You are StockSense AI doing a comprehensive business performance review for a Kirana shop.

INVENTORY DATA:
{inventory_context}

Provide a structured performance analysis covering:
1. **Overall Health Score** (1-10) with justification
2. **Top 3 Actions** the owner should take this week
3. **Revenue Optimization** — which products to push, which to reduce
4. **Risk Alerts** — stockouts, overstocking, expiry risks
5. **Seasonal Advice** — what to prepare for based on current month

Keep it practical and specific. Use the actual product names and quantities from the data.
Format with markdown for readability."""

    text, err = _call_gemma(prompt)
    if err:
        return f"Could not generate analysis: {err}"
    return text
