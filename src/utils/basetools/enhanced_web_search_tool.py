# utils/basetools/enhanced_web_search_tool.py

import requests
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import re
from typing import List

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, description="Maximum number of results to return")
    extract_content: bool = Field(True, description="Whether to extract full content from links")

class SearchResult(BaseModel):
    title: str = Field(..., description="Title of the search result")
    link: str = Field(..., description="URL of the search result")
    content: str = Field("", description="Extracted content from the page")
    summary: str = Field("", description="Brief summary of the content")

class SearchOutput(BaseModel):
    results: List[SearchResult] = Field(..., description="Search results with extracted content")
    search_engine_used: str = Field(..., description="Which search engine was used")
    status: str = Field(..., description="Status of the search operation")

def enhanced_web_search(input: SearchInput) -> SearchOutput:
    """
    Enhanced web search tool that tries Google, Bing, then DuckDuckGo in order
    and extracts content from the resulting pages.
    """
    # Common headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    search_engines = [
        {"name": "Google", "func": _search_google},
        {"name": "Bing", "func": _search_bing},
        {"name": "DuckDuckGo", "func": _search_duckduckgo}
    ]

    for engine in search_engines:
        try:
            print(f"Trying {engine['name']}...")
            results = engine["func"](input.query, input.max_results, headers)

            if results:
                # Extract content if requested
                if input.extract_content:
                    results = _extract_content_from_results(results, headers)

                return SearchOutput(
                    results=results,
                    search_engine_used=engine["name"],
                    status="success"
                )

        except Exception as e:
            print(f"{engine['name']} failed: {str(e)}")
            continue

    return SearchOutput(
        results=[],
        search_engine_used="none",
        status="all_engines_failed"
    )

def _search_google(query: str, max_results: int, headers: dict) -> List[SearchResult]:
    """Search using Google"""
    url = "https://www.google.com/search"
    params = {"q": query, "num": max_results}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Google search failed with status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # Google search result selectors
    for result in soup.select("div.g")[:max_results]:
        title_elem = result.select_one("h3")
        link_elem = result.select_one("a")

        if title_elem and link_elem:
            title = title_elem.get_text()
            link = link_elem.get("href")

            # Clean up Google redirect URLs
            if link and link.startswith("/url?q="):
                link = link.split("/url?q=")[1].split("&")[0]

            if link and not link.startswith("http"):
                continue

            results.append(SearchResult(title=title, link=link))

    return results

def _search_bing(query: str, max_results: int, headers: dict) -> List[SearchResult]:
    """Search using Bing"""
    url = "https://www.bing.com/search"
    params = {"q": query, "count": max_results}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Bing search failed with status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # Bing search result selectors
    for result in soup.select("li.b_algo")[:max_results]:
        title_elem = result.select_one("h2 a")

        if title_elem:
            title = title_elem.get_text()
            link = title_elem.get("href")

            if link and link.startswith("http"):
                results.append(SearchResult(title=title, link=link))

    return results

def _search_duckduckgo(query: str, max_results: int, headers: dict) -> List[SearchResult]:
    """Search using DuckDuckGo"""
    url = "https://duckduckgo.com/html/"
    params = {"q": query}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"DuckDuckGo search failed with status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # DuckDuckGo search result selectors
    for result in soup.select(".result__title a")[:max_results]:
        title = result.get_text()
        link = result.get("href")

        if link and link.startswith("http"):
            results.append(SearchResult(title=title, link=link))

    return results

def _extract_content_from_results(results: List[SearchResult], headers: dict) -> List[SearchResult]:
    """Extract content from search result URLs"""
    enhanced_results = []

    for result in results:
        try:
            # Add delay to avoid being blocked
            time.sleep(random.uniform(1, 3))

            content = _extract_page_content(result.link, headers)
            result.content = content
            result.summary = _generate_summary(content)

            enhanced_results.append(result)

        except Exception as e:
            print(f"Failed to extract content from {result.link}: {str(e)}")
            # Still add the result but without content
            enhanced_results.append(result)

    return enhanced_results

def _extract_page_content(url: str, headers: dict) -> str:
    """Extract clean text content from a webpage"""
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Limit content length
        if len(text) > 3000:
            text = text[:3000] + "..."

        return text

    except Exception:
        return ""

def _generate_summary(content: str) -> str:
    """Generate a brief summary from content"""
    if not content:
        return ""
    
    # Simple summary - first 200 characters
    sentences = content.split('. ')
    summary = sentences[0]
    
    for sentence in sentences[1:]:
        if len(summary + '. ' + sentence) <= 200:
            summary += '. ' + sentence
        else:
            break
    
    return summary + "..." if len(summary) < len(content) else summary