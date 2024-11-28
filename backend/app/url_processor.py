import re
from pathlib import Path
from typing import (
    Optional,
    Union,
)
from urllib.parse import urlparse, urlunparse

import aiohttp
import requests
from bs4 import BeautifulSoup
from langchain.indexes import SQLRecordManager, index
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_redis import RedisVectorStore

from app.config import get_config, get_psql_url
from app.db.db_manager import WebSite

config = get_config()


class UrlProcessor:
    """URL Processor for scraping a website.

    Init args:
        vector_store: The RedisVectorStore to use.
    """

    def __init__(self, vector_store: RedisVectorStore) -> None:
        self.vector_store = vector_store

    def _normalize_url(self, url: str) -> str:
        """Normalize URL"""
        parsed = urlparse(url)
        # Remove any fragments
        parsed = parsed._replace(fragment="")
        # Ensure the path doesn't end with a slash unless it's the root
        if parsed.path.endswith("/") and len(parsed.path) > 1:
            parsed = parsed._replace(path=parsed.path.rstrip("/"))
        return urlunparse(parsed)

    def is_valid_hostname(self, hostname: str) -> bool:
        """Validates a hostname."""
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def _bs4_extractor(self, html: str) -> str:
        """Extract text from html"""
        soup = BeautifulSoup(html, "lxml")
        return re.sub(r"\n\n+", "\n\n", soup.text).strip()

    def _metadata_extractor(
        self, raw_html: str, url: str, response: Union[requests.Response, aiohttp.ClientResponse]
    ) -> dict:
        """Extract metadata from raw html using BeautifulSoup."""
        hostname = urlparse(url).hostname
        content_type = getattr(response, "headers").get("Content-Type", "")
        metadata = {"hostname": hostname, "source": url, "content_type": content_type}

        soup = BeautifulSoup(raw_html, "html.parser")
        if title := soup.find("title"):
            metadata["title"] = title.get_text()
        if description := soup.find("meta", attrs={"name": "description"}):
            metadata["description"] = description.get("content", None)
        if html := soup.find("html"):
            metadata["language"] = html.get("lang", "en-US")
        return metadata

    async def processUrl(
        self, url: str, max_depth: Optional[int] = config["URL_RECURSIVE_MAX_DEPTH"]
    ) -> str:
        """Process a URL.

        Args:
            url: The url to to process
            max_depth: Optional number for the max depth for recursively loading webpages.

        Returns:
            str: The hostname of the url
        """
        # Validate URL
        normalized_url = self._normalize_url(url)
        parsed = urlparse(normalized_url)

        if parsed.scheme == "https":
            hostname = parsed.hostname
        elif parsed.scheme == "" and self.is_valid_hostname(normalized_url):
            hostname = normalized_url
            normalized_url = f"https://{normalized_url}"
        elif parsed.scheme == "" and not self.is_valid_hostname(normalized_url):
            path = Path(normalized_url)
            hostname = path.parts[0]
            normalized_url = f"https://{normalized_url}"

        else:
            raise ValueError("Unsupported url schema")

        # Assume https
        base_url = f"https://{hostname}"

        # Create website in db if necessary
        existing_web_page = WebSite.get_or_none(WebSite.hostname == hostname)
        if existing_web_page is None:
            WebSite.create(hostname=hostname, base_url=base_url)

        # TODO: Check robots.txt first
        # TODO: Check Sitemaps if available
        loader = RecursiveUrlLoader(
            url=normalized_url,
            base_url=base_url,
            max_depth=max_depth,
            extractor=self._bs4_extractor,
            metadata_extractor=self._metadata_extractor,
            exclude_dirs=(
                [
                    f"{base_url}/cart",
                    f"{base_url}/wp-includes",
                    f"{base_url}/wp-content",
                    f"{base_url}/wp-json",
                    f"{base_url}/xmlrpc.php",
                ]
            ),
        )
        index(
            loader,
            SQLRecordManager(namespace=f"redis/{hostname}", db_url=get_psql_url()),
            self.vector_store,
            cleanup="incremental",
            source_id_key="source",
        )
        return hostname
