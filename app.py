from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI, OpenAIError
from fastapi.middleware.cors import CORSMiddleware
import base64
import json
import difflib
import os


openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ OPENAI_API_KEY environment variable not set. Exiting...")
    import sys
    sys.exit(1)

client = OpenAI(api_key=openai_key)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Virtual TA! Use /api/ for queries."}

try:
    with open("data/discourse_posts.json") as f:
        discourse_data = json.load(f)
except Exception as e:
    print("❌ Failed to load discourse_posts.json:", e)
    discourse_data = []

try:
    with open("data/course_content.txt") as f:
        course_data = f.read()
except Exception as e:
    print("❌ Failed to load course_content.txt:", e)
    course_data = ""


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
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
        except OpenAIError as oe:
            print("❌ OpenAI API Error:", oe)
            return {"error": str(oe)}
        print("✅ OpenAI Response Received")

        links = [
            d for d in discourse_data
            if query.question.lower() in d["content"].lower()
        ]
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


