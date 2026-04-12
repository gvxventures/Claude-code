"""
Estate Planning Document Fetcher
Logs into ask.precepts-esp.com and downloads all articles/documents.

Requirements:
    pip install requests beautifulsoup4 lxml

Run:
    python fetch_estate_docs.py
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://ask.precepts-esp.com"
LOGIN_URL = f"{BASE_URL}/login"
DOCS_URL  = f"{BASE_URL}/document"

EMAIL    = os.environ.get("ESP_EMAIL", "")
PASSWORD = os.environ.get("ESP_PASSWORD", "")

if not EMAIL or not PASSWORD:
    import getpass
    EMAIL    = input("Email: ").strip()
    PASSWORD = getpass.getpass("Password: ")

OUTPUT_DIR = "estate_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def login(session: requests.Session) -> bool:
    """Log in and return True on success."""
    # 1. GET login page to grab CSRF token (if any)
    r = session.get(LOGIN_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # Collect all hidden fields (CSRF tokens, etc.)
    payload = {}
    form = soup.find("form")
    if form:
        for inp in form.find_all("input", {"type": "hidden"}):
            payload[inp.get("name", "")] = inp.get("value", "")

    payload["email"]    = EMAIL
    payload["password"] = PASSWORD

    # Some sites use 'username' instead of 'email'
    if form:
        for inp in form.find_all("input"):
            name = inp.get("name", "").lower()
            if "user" in name and "email" not in name:
                payload[name] = EMAIL

    # 2. POST credentials
    post_url = BASE_URL + form.get("action", "/login") if form else LOGIN_URL
    r2 = session.post(post_url, data=payload, headers=HEADERS, timeout=20, allow_redirects=True)
    r2.raise_for_status()

    # Check if login succeeded (no longer on login page)
    if "/login" not in r2.url and "login" not in r2.text.lower()[:200]:
        print("✓ Login successful")
        return True

    # Try JSON login as fallback
    print("  Form login may have failed, trying JSON login...")
    r3 = session.post(
        LOGIN_URL,
        json={"email": EMAIL, "password": PASSWORD},
        headers={**HEADERS, "Content-Type": "application/json"},
        timeout=20,
        allow_redirects=True,
    )
    if r3.status_code < 400 and "/login" not in r3.url:
        print("✓ JSON Login successful")
        return True

    print("✗ Login failed — check credentials or site structure")
    print("  Final URL:", r2.url)
    return False


def get_all_document_links(session: requests.Session) -> list[dict]:
    """Scrape the /document page for all article links."""
    links = []
    page = 1

    while True:
        url = f"{DOCS_URL}?page={page}" if page > 1 else DOCS_URL
        r = session.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # Collect all <a> tags that look like article links
        found = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            # Adjust this filter based on site URL patterns
            if href.startswith("/document/") or "/article/" in href or "/doc/" in href:
                full_url = BASE_URL + href if href.startswith("/") else href
                if {"url": full_url, "title": text} not in links:
                    links.append({"url": full_url, "title": text})
                    found += 1

        print(f"  Page {page}: found {found} links (total {len(links)})")
        if found == 0:
            break

        # Check for a "next" pagination link
        next_link = soup.find("a", string=lambda t: t and "next" in t.lower())
        if not next_link:
            break
        page += 1
        time.sleep(0.5)

    return links


def fetch_article(session: requests.Session, url: str) -> str:
    """Fetch a single article and return its text content."""
    r = session.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # Remove nav/footer/script noise
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Try common content containers
    for selector in ["article", "main", ".content", ".article-body", "#content", ".post-body"]:
        container = soup.select_one(selector)
        if container:
            return container.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)


def save_article(title: str, url: str, text: str, index: int):
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:80]
    filename = os.path.join(OUTPUT_DIR, f"{index:03d}_{safe_title}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\nURL: {url}\n{'='*60}\n\n{text}")
    return filename


def main():
    session = requests.Session()

    if not login(session):
        print("\nHint: Open DevTools in your browser, log in manually, copy the")
        print("      session cookie, and add it to the script as:")
        print("      session.cookies.set('session', '<your-cookie-value>')")
        return

    print(f"\nFetching document list from {DOCS_URL} ...")
    links = get_all_document_links(session)

    if not links:
        # Dump the raw page for debugging
        r = session.get(DOCS_URL, headers=HEADERS)
        with open("debug_document_page.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        print("No document links found. Saved raw HTML to debug_document_page.html")
        print("Please share that file so the link selectors can be tuned.")
        return

    print(f"\nFound {len(links)} documents. Downloading...\n")
    summary_index = []

    for i, doc in enumerate(links, 1):
        print(f"[{i}/{len(links)}] {doc['title'][:60]}")
        try:
            text = fetch_article(session, doc["url"])
            filename = save_article(doc["title"], doc["url"], text, i)
            summary_index.append({"index": i, "title": doc["title"], "url": doc["url"], "file": filename})
            time.sleep(0.3)  # polite delay
        except Exception as e:
            print(f"  ERROR: {e}")

    # Save index
    index_path = os.path.join(OUTPUT_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(summary_index, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Done! {len(summary_index)} documents saved to '{OUTPUT_DIR}/'")
    print(f"  Index saved to {index_path}")
    print("\nNext step: Share the contents of the 'estate_docs/' folder here")
    print("and I will build your 3-day estate planning study plan.")


if __name__ == "__main__":
    main()
