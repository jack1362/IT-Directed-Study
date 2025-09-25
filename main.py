import requests
import csv
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

TAG_BLACKLIST = ["script", "style", "header", "footer", "nav", "aside", "noscript"]
TAG_WHITELIST = ["p", "h1", "h2"]

def extractArticle(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    for tag in soup(TAG_BLACKLIST):
        tag.decompose()

    article = soup.find("article")
    if article:
        textElements = article.find_all(TAG_WHITELIST)
    else:
        textElements = soup.find_all(TAG_WHITELIST)

    piecesOfText = []
    for element in textElements:
        piece = element.get_text(strip=True)
        if piece:
            piecesOfText.append(piece)
    
    text = "\n".join(piecesOfText)
    return text if text else None

def saveArticle(url, label, filename="dataset.csv"):
    existing_urls = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                existing_urls.add(row[2])

    if url in existing_urls:
        print(f"SKIPPED DUPLICATE ARTICLE: {url}")
        return
    
    try:
        text = extractArticle(url)
        # Only save if it looks like a real article
        if text and len(text.split()) > 100:
            with open(filename, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([text, label, url])
            print(f"{label} SAVED: {url}")
    except Exception as e:
        print(f"ERROR TRYING TO SAVE {url}: {e}")

def getLinks(url, domain_only=True):
    """Extract links from a given page."""
    links = set()
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return links

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(url, href)
            
            if domain_only:
                if urlparse(full_url).netloc != urlparse(url).netloc:
                    continue

            if full_url.startswith("http"):
                links.add(full_url)
    except Exception as e:
        print(f"ERROR extracting links from {url}: {e}")
    return links

def isArticleURL(url):
    """Heuristic to decide if a URL is likely an article."""
    # Example: NYTimes Athletic articles have /YYYY/MM/ or end with slug-like IDs
    if any(x in url for x in ["/live-blogs/", "/202", "/article/", "/story/"]):
        return True
    return False

def crawlAndSave(start_url, label, max_pages=50):
    """Crawl starting from a URL and save articles."""
    visited = set()
    to_visit = [start_url]

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        # Save only if it looks like an article
        if isArticleURL(url):
            saveArticle(url, label)

        # Always extract new links (even from sections)
        new_links = getLinks(url)
        for link in new_links:
            if link not in visited:
                to_visit.append(link)

# Example: crawl up to 50 pages, but only save real articles
crawlAndSave(
    "https://www.nytimes.com/athletic/live-blogs/transfer-news-live-updates-thursday-august-28/qNI2Vf8dydwk/",
    "REAL",
    max_pages=50
)