import requests
from bs4 import BeautifulSoup
from models import db, Opportunity
from classifier import classify
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def save_opportunity(title, university, link):
    if not Opportunity.query.filter_by(title=title).first():
        domain = classify(title)
        opp = Opportunity(
            title=title,
            university=university,
            domain=domain,
            link=link,
            posted_at=datetime.utcnow()
        )
        db.session.add(opp)
        db.session.commit()


def scrape_harvard():
    url = "https://news.harvard.edu/gazette/section/science-and-tech/"
    r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, "lxml")

    articles = soup.find_all("h2")
    for a in articles[:8]:
        title = a.get_text(strip=True)
        save_opportunity(title, "Harvard University", url)


def scrape_yale():
    url = "https://news.yale.edu/"
    r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, "lxml")

    headlines = soup.find_all("h3")
    for h in headlines[:8]:
        title = h.get_text(strip=True)
        save_opportunity(title, "Yale University", url)


def scrape_princeton():
    url = "https://www.princeton.edu/news"
    r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, "lxml")

    headlines = soup.find_all("h2")
    for h in headlines[:8]:
        title = h.get_text(strip=True)
        save_opportunity(title, "Princeton University", url)


def scrape_all():
    scrape_harvard()
    scrape_yale()
    scrape_princeton()