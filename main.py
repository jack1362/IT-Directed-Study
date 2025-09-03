import requests
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

print(extractArticle("https://www.nytimes.com/athletic/live-blogs/transfer-news-live-updates-thursday-august-28/qNI2Vf8dydwk/"))