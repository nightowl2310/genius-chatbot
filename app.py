print("APP VERSION 5")

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
COACHING_WEBSITE_URL = "https://genius-tutorial.vercel.app"

def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
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

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.0-pro")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Backend is working"})
    full_prompt = SYSTEM_PROMPT + "\nStudent: " + user_message
    response = model.generate_content(full_prompt)
    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)