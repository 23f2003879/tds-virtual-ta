import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from my_cookies import _t, _forum_session

def create_session():
    domain = "discourse.onlinedegree.iitm.ac.in"
    session = requests.Session()
    session.cookies.set('_t', _t, domain=domain)
    session.cookies.set('_forum_session', _forum_session, domain=domain)
    return session

def scrape_discourse_posts(save_path="data/discourse_posts.json"):
    session = create_session()
    
    base_url = "https://discourse.onlinedegree.iitm.ac.in"
    category_url = f"{base_url}/c/courses/tds-kb/34.json"

    print("Fetching topic list...")
    r = session.get(category_url)
    if r.status_code != 200:
        print(f"[❌] Failed to fetch category JSON. Status: {r.status_code}")
        return

    try:
        topics = r.json()["topic_list"]["topics"]
    except Exception as e:
        print("[❌] Error parsing topics:", e)
        return

    posts = []

    print("Fetching posts from each topic...")
    for topic in tqdm(topics):
        topic_id = topic["id"]
        slug = topic["slug"]
        topic_title = topic["title"]

        topic_url = f"{base_url}/t/{slug}/{topic_id}.json"
        res = session.get(topic_url)
        if res.status_code != 200:
            print(f"[⚠️] Skipping {topic_url} (status {res.status_code})")
            continue

        topic_data = res.json()
        for post in topic_data["post_stream"]["posts"]:
            cleaned_text = BeautifulSoup(post["cooked"], "html.parser").text
            posts.append({
                "topic": topic_title,
                "url": f"{base_url}/t/{slug}/{topic_id}/{post['post_number']}",
                "content": cleaned_text
            })

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)
        print(f"[✅] Discourse posts saved to {save_path}")

if __name__ == "__main__":
    scrape_discourse_posts()