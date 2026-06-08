from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google import genai

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
COACHING_WEBSITE_URL = "https://genius-tutorial.vercel.app"

import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except:
        return "Website info not available."

website_text = scrape_website(COACHING_WEBSITE_URL)

SYSTEM_PROMPT = f"""
You are a helpful assistant for Genius Tutorial coaching centre.
Here is all the information scraped from the website:

{website_text[:3000]}

Answer only based on this information.
If you don't know something, say: 'Please contact us directly for more info.'
Keep answers short, friendly, and to the point.
"""

client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/models", methods=["GET"])
def list_models():
    models = [m.name for m in client.models.list()]
    return jsonify({"models": models})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Please ask something."})
    full_prompt = SYSTEM_PROMPT + "\nStudent: " + user_message
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # ✅ correct
        contents=full_prompt
    )
    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)