import requests
import csv
import os
from bs4 import BeautifulSoup

TAG_BLACKLIST = ["script", "style", "header", "footer", "nav", "aside", "noscript"]
TAG_WHITELIST = ["p", "h1", "h2"]

def extractArticle(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return "Failed to fetch page"
    
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

    return text

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
        if text and len(text.split()) > 50:
            with open(filename, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([text, label, url])
            print(f"{label} SAVED: {url}")
    except:
        print(f"ERROR TRYING TO SAVE {url}")


saveArticle("https://www.nytimes.com/athletic/live-blogs/transfer-news-live-updates-thursday-august-28/qNI2Vf8dydwk/", "REAL")