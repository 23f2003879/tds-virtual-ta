from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
import base64
import openai
import json
import difflib
import os
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

with open("data/discourse_posts.json") as f:
    discourse_data = json.load(f)

with open("data/course_content.txt") as f:
    course_data = f.read()

class Query(BaseModel):
    question: str
    image: Optional[str] = None

@app.post("/api/")
async def respond(query: Query):
    try:
        print("✅ Received Query:", query.question)

        if query.image:
            print("🖼️ Decoding image...")
            with open("temp_image.webp", "wb") as f:
                f.write(base64.b64decode(query.image))

        print("🧠 Preparing prompt...")
        context = "\n\n".join([post["content"] for post in discourse_data[:20]])
        prompt = f"""
You are a TDS Teaching Assistant. Answer the following question clearly and concisely.
Question: {query.question}

Course Content: {course_data[:1000]}
Discourse Posts (Sample):
{context[:2000]}
"""
        print("📡 Sending prompt to OpenAI...")

        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query.question}],
            temperature=0.3
        )

        print("✅ OpenAI Response Received")

        links = [d for d in discourse_data if query.question.lower() in d["content"].lower()]
        response_links = [{"url": l["url"], "text": l["content"][:80]} for l in links[:2]]

        return {
            "answer": response.choices[0].message.content,
            "links": response_links
        }

    except Exception as e:
        print("❌ ERROR IN API:", e)
        return {"error": str(e)}


    

def search_relevant_posts(question):
    """Finds closest Discourse posts based on the query."""
    best_matches = difflib.get_close_matches(question, [d["content"] for d in discourse_data], n=2)
    return [{"url": d["url"], "text": d["content"][:80]} for d in discourse_data if d["content"] in best_matches]


