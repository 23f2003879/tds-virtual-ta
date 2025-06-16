from playwright.sync_api import sync_playwright
import time
import os

def scrape_tds_course_content(output_path="data/course_content.txt"):
    os.makedirs("data", exist_ok=True)  

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to page...")
        page.goto("https://tds.s-anand.net/#/2025-01/")
        print("Waiting for content to load...")
        time.sleep(5) 

        print("Extracting content...")
        content = page.locator("main").inner_text()
        browser.close()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"[✅] Course content saved to {output_path}")

if __name__ == "__main__":
    scrape_tds_course_content()
