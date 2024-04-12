"""Web crawler with depth control."""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

logger = logging.getLogger(__name__)


def _substack_reader(soup: Any, **kwargs) -> Tuple[str, Dict[str, Any]]:
    """Extract text from Substack blog post."""
    extra_info = {
        "Title of this Substack post": soup.select_one("h1.post-title").getText(),
        "Subtitle": soup.select_one("h3.subtitle").getText(),
        "Author": soup.select_one("span.byline-names").getText(),
    }
    text = soup.select_one("div.available-content").getText()
    return text, extra_info


def _readthedocs_reader(soup: Any, url: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
    """Extract text from a ReadTheDocs documentation site"""
    import requests
    from bs4 import BeautifulSoup

    links = soup.find_all("a", {"class": "reference internal"})
    rtd_links = []

    for link in links:
        rtd_links.append(link["href"])
    for i in range(len(rtd_links)):
        if not rtd_links[i].startswith("http"):
            rtd_links[i] = urljoin(url, rtd_links[i])

    texts = []
    for doc_link in rtd_links:
        page_link = requests.get(doc_link)
        soup = BeautifulSoup(page_link.text, "html.parser")
        try:
            text = soup.find(attrs={"role": "main"}).get_text()

        except IndexError:
            text = None
        if text:
            texts.append("\n".join([t for t in text.split("\n") if t]))
    return "\n".join(texts), {}


def _readmedocs_reader(
        soup: Any, url: str, include_url_in_text: bool = True
) -> Tuple[str, Dict[str, Any]]:
    """Extract text from a ReadMe documentation site"""
    import requests
    from bs4 import BeautifulSoup

    links = soup.find_all("a")
    docs_links = [link["href"] for link in links if "/docs/" in link["href"]]
    docs_links = list(set(docs_links))
    for i in range(len(docs_links)):
        if not docs_links[i].startswith("http"):
            docs_links[i] = urljoin(url, docs_links[i])

    texts = []
    for doc_link in docs_links:
        page_link = requests.get(doc_link)
        soup = BeautifulSoup(page_link.text, "html.parser")
        try:
            text = ""
            for element in soup.find_all("article", {"id": "content"}):
                for child in element.descendants:
                    if child.name == "a" and child.has_attr("href"):
                        if include_url_in_text:
                            url = child.load("href")
                            if url is not None and "edit" in url:
                                text += child.text
                            else:
                                text += (
                                    f"{child.text} (Reference url: {doc_link}{url}) "
                                )
                    elif child.string and child.string.strip():
                        text += child.string.strip() + " "

        except IndexError:
            text = None
            logger.error(f"Could not extract text from {doc_link}")
            continue
        texts.append("\n".join([t for t in text.split("\n") if t]))
    return "\n".join(texts), {}


def _gitbook_reader(
        soup: Any, url: str, include_url_in_text: bool = True
) -> Tuple[str, Dict[str, Any]]:
    """Extract text from a ReadMe documentation site"""
    import requests
    from bs4 import BeautifulSoup

    links = soup.find_all("a")
    docs_links = [link["href"] for link in links if "/docs/" in link["href"]]
    docs_links = list(set(docs_links))
    for i in range(len(docs_links)):
        if not docs_links[i].startswith("http"):
            docs_links[i] = urljoin(url, docs_links[i])

    texts = []
    for doc_link in docs_links:
        page_link = requests.get(doc_link)
        soup = BeautifulSoup(page_link.text, "html.parser")
        try:
            text = soup.find("main")
            clean_text = ", ".join([tag.get_text() for tag in text])
        except IndexError:
            text = None
            logger.error(f"Could not extract text from {doc_link}")
            continue
        texts.append(clean_text)
    return "\n".join(texts), {}


DEFAULT_WEBSITE_EXTRACTOR: Dict[
    str, Callable[[Any, str], Tuple[str, Dict[str, Any]]]
] = {
    "substack.com": _substack_reader,
    "readthedocs.io": _readthedocs_reader,
    "readme.com": _readmedocs_reader,
    "gitbook.io": _gitbook_reader,
}


def is_downloadable(url):
    response = requests.get(url, stream=True)

    headers = response.headers

    content_type = headers.get('Content-Type', '')
    content_disposition = headers.get('Content-Disposition', '')

    if 'attachment' in content_disposition:
        logger.info(f"The URL points to a downloadable file: {url}")
        return True
    elif any(file_type in content_type for file_type in ['application', 'image', 'audio', 'video']):
        logger.info(f"The URL points to a file based on Content-Type: {url}")
        return True
    else:
        return False


class WebCrawler(BaseReader):
    """BeautifulSoup web page crawler.

    Reads pages from the web.
    Requires the `bs4` and `urllib` packages.

    Args:
        website_extractor (Optional[Dict[str, Callable]]): A mapping of website
            hostname (e.g. google.com) to a function that specifies how to
            extract text from the BeautifulSoup obj. See DEFAULT_WEBSITE_EXTRACTOR.
        depth (int): Depth of the crawler. If 0, no crawling is performed.
    """

    def __init__(
            self,
            website_extractor: Optional[Dict[str, Callable]] = None,
            depth: int = 0,
    ) -> None:
        """Initialize with parameters."""
        self.website_extractor = website_extractor or DEFAULT_WEBSITE_EXTRACTOR
        self.depth = depth
        self.scanned_urls = set()

    def load_data(
            self,
            urls: List[str],
            custom_hostname: Optional[str] = None,
            include_url_in_text: Optional[bool] = True,
    ) -> List[Document]:
        """Load data from the urls.

        Args:
            urls (List[str]): List of URLs to scrape.
            custom_hostname (Optional[str]): Force a certain hostname in the case
                a website is displayed under custom URLs (e.g. Substack blogs)
            include_url_in_text (Optional[bool]): Include the reference url in the text of the document

        Returns:
            List[Document]: List of documents.
        """
        documents = []
        for url in urls:
            url_documents = self._crawl_url(url, custom_hostname, include_url_in_text)
            documents.extend(url_documents)

        return documents

    def _crawl_url(self, url, custom_hostname, include_url_in_text, cur_depth=0):
        if cur_depth > self.depth or is_downloadable(url):
            # stop condition
            return []

        # setup
        try:
            page = requests.get(url)
            self.scanned_urls.add(url)
            logger.info(f"Processing '{url}' URL.")
        except Exception as e:
            # soft fail, log and continue with other URLs
            logger.warning(f"{str(e)} error occurred while processing '{url}' URL.")
            return []

        hostname = custom_hostname or urlparse(url).hostname
        soup = BeautifulSoup(page.content, "html.parser")

        # recursive link construction (crawling)
        documents = []
        links = soup.find_all("a", href=True)
        for link in links:
            sub_url = urljoin(url, urlparse(link['href']).path)
            if hostname == urlparse(sub_url).hostname and sub_url not in self.scanned_urls:
                # only crawl if we are on the same domain
                sub_documents = self._crawl_url(
                    sub_url,
                    custom_hostname,
                    include_url_in_text,
                    cur_depth + 1
                )
                documents.extend(sub_documents)

        # current page parsing
        document = self._parse_document(url, hostname, include_url_in_text, soup)
        documents.append(document)

        return documents

    def _parse_document(self, url, hostname, include_url_in_text, soup):
        extra_info = {"URL": url}
        if hostname in self.website_extractor:
            data, metadata = self.website_extractor[hostname](
                soup=soup, url=url, include_url_in_text=include_url_in_text
            )
            extra_info.update(metadata)

        else:
            data = soup.getText()

        return Document(text=data, extra_info=extra_info)
