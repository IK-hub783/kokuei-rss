import requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

BASE_URL = "https://www.kokuei-film.com/blog/maiika/"

def fetch_articles():
    response = requests.get(BASE_URL, timeout=10)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for article in soup.select("div.blog-list a"):
        link = article.get("href")
        title = article.select_one("h3")
        date = article.select_one("span.date")

        if not (link and title and date):
            continue

        pub_date = datetime.strptime(date.text.strip(), "%Y.%m.%d")
        pub_date_str = pub_date.strftime("%a, %d %b %Y 00:00:00 +0900")

        articles.append({
            "title": title.text.strip(),
            "link": link if link.startswith("http") else BASE_URL.rstrip("/") + "/" + link.lstrip("/"),
            "pubDate": pub_date_str
        })

        if len(articles) >= 10:
            break

    return articles

def generate_rss(articles):
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')

    SubElement(channel, 'title').text = "まーイーカ2 - 国映映画研究部"
    SubElement(channel, 'link').text = BASE_URL
    SubElement(channel, 'description').text = "映画作家いまおかしんじによる連載ブログ"
    SubElement(channel, 'language').text = "ja"

    for post in articles:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post["title"]
        SubElement(item, 'link').text = post["link"]
        SubElement(item, 'guid').text = post["link"]
        SubElement(item, 'pubDate').text = post["pubDate"]

    return minidom.parseString(tostring(rss)).toprettyxml(indent="  ")

if __name__ == "__main__":
    articles = fetch_articles()
    rss_xml = generate_rss(articles)

    with open("maiika2_feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_xml)
