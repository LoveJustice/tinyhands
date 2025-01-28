#!/usr/bin/env python3
"""
Module for targeted news article search and filtering related to trafficking incidents.

Refactored to exclude async usage and concurrency references.

Usage:
    python google_miner.py --days_back 7
"""
import csv
import argparse
import logging
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlparse
import tldextract
from googlesearch import search  # Ensure you are using the correct googlesearch package.
import json
import os

from libraries.neo4j_lib import execute_neo4j_query



logging.basicConfig(
    filename="trafficking_news.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.info("Google Miner service started (refactored, sync version).")


# URL = st.text_input("Enter Article URL", key="search_url")
def extract_main_text_selenium(driver, url: str) -> str:
    """
    Extracts the main text from a given URL using Selenium.

    Args:
        url (str): The URL of the article to extract.

    Returns:
        str: The main text of the article.
    """
    try:


        # Adjust the CSS selector based on the website's structure
        try:
            article_body = driver.find_element("css selector", "div.detail-content")
            text = article_body.text
            logger.info("Main article content extracted successfully.")
        except Exception:
            # Fallback to extracting all body text
            text = driver.find_element("tag name", "body").text
            logger.warning(
                "Specific article content not found; extracted entire body text."
            )


        return text
    except Exception as e:
        logger.error(f"Selenium extraction failed for URL {url}: {e}")
        return ""

# ------------------------------
# TraffickingNewsSearch Class Definition
# ------------------------------
class TraffickingNewsSearch:
    """Encapsulates news article search logic related to trafficking incidents."""
    def __init__(self, search_config: dict) -> None:
        self.search_name = search_config['id']
        self.days_back = search_config['days_back']

        self.excluded_domains = {}
        #     # News aggregators and feeds
        #     "oxfordlearnersdictionaries.com",
        #     "amazon.com",
        #     "news.google.com",
        #     "news.yahoo.com",
        #     "headtopics.com",
        #     "bignewsnetwork.com",
        #     "europeansting.com",
        #     "webindia123.com",
        #     # Podcasts and media platforms
        #     "podcasts.apple.com",
        #     "policing.tv",
        #     # Study and education platforms
        #     "studocu.com",
        #     # Forums and community sites
        #     "nairaland.com",
        #     "bulawayo24.com",
        #     # NGO and international organization job boards
        #     "reliefweb.int",
        #     "uncareer.net",
        #     "unjobnet.org",
        #     "ngojobsinafrica.com",
        #     "jobs.undp.org",
        #     "youropportunitiesafrica.com",
        #     # Legal and case databases
        #     "caselaw.ihrda.org",
        #     "complianceweek.com",
        #     # Document repositories and databases
        #     "ftp.dontforgettofeedme.org",
        #     "kpmg.com",
        #     # Generic content sites
        #     "blackfacts.com",
        #     "worldrainforests.com",
        #     "thesovereignstate.org",
        #     "africanwildlifeplains.com",
        #     "thegreatestbooks.org",
        #     # Corporate career sites
        #     "hitachienergy.com",
        #     "dbschenker.com",
        #     # Job and career sites
        #     "indeed.com",
        #     "monster.com",
        #     "glassdoor.com",
        #     "careers.org",
        #     "careerbuilder.com",
        #     "dice.com",
        #     "workday.com",
        #     "jobs.com",
        #     "simplyhired.com",
        #     "ziprecruiter.com",
        #     "reed.co.uk",
        #     "seek.com.au",
        #     "jobstreet.com",
        #     "timesjobs.com",
        #     "naukri.com",
        #     "recruit.com",
        #     # Social media
        #     "facebook.com",
        #     "twitter.com",
        #     "instagram.com",
        #     "youtube.com",
        #     "reddit.com",
        #     "pinterest.com",
        #     "linkedin.com",
        #     # Academic/Research
        #     "academia.edu",
        #     "researchgate.net",
        #     "scholar.google.com",
        #     "jstor.org",
        #     "springer.com",
        #     "sciencedirect.com",
        #     "nature.com",
        #     "tandfonline.com",
        #     "wiley.com",
        #     "oxford.com",
        #     "cambridge.org",
        #     # Wiki/Knowledge bases
        #     "wikipedia.org",
        #     "wikimedia.org",
        #     "scholarpedia.org",
        #     # Government domains (partial matches)
        #     ".gov",
        #     ".mil",
        #     ".edu",
        #     ".org",
        #     # Research organizations
        #     "who.int",
        #     "worldbank.org",
        #     "un.org",
        #     "unesco.org",
        #     "unicef.org",
        #     "nih.gov",
        #     "cdc.gov",
        #     "europa.eu",
        # }

        self.academic_suffixes = {}
        # {
        #     "ac.uk",
        #     "edu.au",
        #     "ac.jp",
        #     "edu.cn",
        #     "ac.za",
        #     "edu.sg",
        #     "ac.nz",
        #     "edu.hk",
        #     "ac.in",
        #     "edu.my",
        #     "ac.ir",
        #     "edu.br",
        # }

        self.trafficking_terms = [
            '"human trafficking"',
            '"cyber trafficking"',
            '"child trafficking"',
            '"forced labor"',
            '"sexual exploitation"',
            '"organ trafficking"',
        ]

        self.evidence_terms = [
            "arrest",
            "suspect",
            "victim",
            "rescue",
            "operation",
            "investigation",
            "prosecute",
            "charged",
            "convicted",
        ]

    def is_valid_news_domain(self, url: str) -> bool:
        """
        Filter out non-news domains including government, academic, and research sites.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Check for excluded domains
            if any(excluded in domain for excluded in self.excluded_domains):
                return False

            if any(domain.endswith(suffix) for suffix in self.academic_suffixes):
                return False

            institutional_keywords = {
                "research",
                "university",
                "institute",
                "college",
                "laboratory",
                "academic",
                "scholar",
                "science",
            }
            institutional_keywords={}
            generic_content_keywords = {
                "summaries",
                "database",
                "evaluation",
                "library",
                "archive",
                "repository",
                "topics",
                "category",
                "index-id",
                "filter",
                "tag",
                "author",
                "page",
                "news-headlines",
                "local-hard-news",
                "in-brief",
            }
            generic_content_keywords={}
            content_sections = {
                "crime-and-courts",
                "news/state",
                "news/community",
                "news/local",
                "news_headlines",
                "crime_courts",
                "state_and_regional",
            }
            content_sections={}
            career_keywords = {
                "jobs",
                "career",
                "careers",
                "employment",
                "recruit",
                "recruiting",
                "staffing",
                "vacancy",
                "vacancies",
                "job-search",
                "jobsite",
                "workforce",
                "talent",
                "hire",
                "hiring",
            }
            career_keywords={}
            if any(keyword in domain for keyword in institutional_keywords):
                return False
            if any(keyword in domain for keyword in career_keywords):
                return False

            path = parsed.path.lower()
            if any(keyword in path for keyword in generic_content_keywords):
                return False
            if any(section in path for section in content_sections):
                return False

            if (
                "/page/" in path
                or "page=" in parsed.query
                or "/tag/" in path
                or "/category/" in path
                or "/topics/" in path
                or "/author/" in path
                or "/archive" in path
            ):
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking domain validity for {url}: {e}")
            return False

    def construct_query(self, start_date: str, end_date: str, include_evidence_terms: bool = True) -> str:
        """
        Construct a targeted search query.
        """
        negative_keywords = [
            "-jobs",
            "-career",
            "-careers",
            "-vacancy",
            "-hiring",
            "-recruitment",
            "-position",
            "-employment",
        ]
        negative_keywords=[]
        extended_negative_keywords = [
            "-politics",
            "-minister",
            "-election",
            "-president",
            "-campaign",
            "-senate",
            "-prime-minister",
            "-parliament",
            "-celebrity",
            "-gossip",
            "-scandal",
        ]
        extended_negative_keywords=[]
        all_negative_keywords = negative_keywords + extended_negative_keywords
        negative_terms = " ".join(all_negative_keywords)

        trafficking_part = f"({' OR '.join(self.trafficking_terms)}) {negative_terms}"

        if include_evidence_terms:
            evidence_part = f"({' OR '.join(self.evidence_terms)})"
            base_query = f'{trafficking_part} AND {evidence_part} AND ("news" OR "article") AND "South Africa"'
        else:
            base_query = f'{trafficking_part}'

        excluded_sites = " ".join(
            [f"-site:{domain}" for domain in self.excluded_domains if not domain.startswith(".")]
        )

        # Combine query segments; if date filtering causes issues, you might remove these filters.
        final_query = f"{base_query} {excluded_sites} after:{start_date} before:{end_date}"
        logger.debug(f"Constructed query: {final_query}")
        return final_query

    def fetch_articles(self, query: str, max_results: int = 200) -> List[str]:
        """
        Fetch articles synchronously using google search.
        """
        articles = []
        try:
            # Using parameters accepted by the module:
            # - tld: search domain extension (e.g., "com")
            # - lang: language (e.g., "en")
            # - num: number of results per page
            # - start: starting index
            # - stop: final index (non-inclusive)
            # - pause: seconds to wait between requests
            for url in search(query, tld="com", lang="en", num=10, start=0, stop=max_results, pause=2):
                if self.is_valid_news_domain(url):
                    articles.append(url)
            return articles
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []

    def get_recent_articles(self) -> List[str]:
        """
        Retrieve recent articles based on days_back in the configuration.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days_back)

        query = self.construct_query(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        logger.info(f"Searching for articles with query: {query}")
        return self.fetch_articles(query)

    def save_to_neo4j(self, urls: List[str]) -> None:
        """
        Save filtered articles to Neo4j database.
        """
        query = """
            MERGE (url:Url {url: $url, source: 'google_miner'})
            WITH url
            MERGE (domain:Domain { name: $domain_name })
            MERGE (url)-[:HAS_DOMAIN]->(domain)
        """
        for url in urls:
            extracted = tldextract.extract(url)
            domain_name = extracted.domain
            parameters = {"domain_name": domain_name, "url": url}
            execute_neo4j_query(query, parameters)
            logger.info(f"Saved URL to Neo4j: {url}")

    def save_to_csv(self, urls: List[str]) -> None:
        """
        Save filtered articles to a CSV file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_name = f"{output_dir}/saved_urls_{self.search_name}_{timestamp}.csv"

        with open(file_name, mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["url", "domain_name", "source"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for url in urls:
                extracted = tldextract.extract(url)
                domain_name = extracted.domain
                writer.writerow({
                    "url": url,
                    "domain_name": domain_name,
                    "source": "google_miner"
                })
                logger.info(f"Saved URL to CSV: {url}")

        logger.info(f"CSV file '{file_name}' created successfully.")

