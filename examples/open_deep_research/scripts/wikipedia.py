from datetime import datetime
from typing import Optional

import requests


def search_wikipedia(query: str, lang: str = "en", before: Optional[str] = None) -> dict:
    """
    Search Wikipedia articles

    Args:
        query (str): Search query
        lang (str, optional): Language code. Defaults to "en".
        before (str, optional): Date in YYYY-MM-DD format. If provided, will return the latest revision before this date.

    Returns:
        dict: Search results containing title, extract, and URL
    """
    base_url = f"https://{lang}.wikipedia.org/w/api.php"

    # First search for the page
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "utf8": 1,
    }

    search_response = requests.get(base_url, params=search_params)
    search_data = search_response.json()

    if not search_data["query"]["search"]:
        return {"error": "No results found"}

    # Get the first result
    first_result = search_data["query"]["search"][0]
    page_id = first_result["pageid"]

    # Get page content
    content_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|info|revisions",
        "pageids": page_id,
        "exintro": 1,
        "explaintext": 1,
        "inprop": "url",
        "rvprop": "ids|timestamp|content",
        "rvlimit": 1,
    }

    if before:
        try:
            # Convert date to timestamp
            timestamp = datetime.strptime(before, "%Y-%m-%d").strftime("%Y%m%d%H%M%S")
            content_params["rvstart"] = timestamp
            content_params["rvdir"] = "older"  # Get the first revision before this date
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD"}

    content_response = requests.get(base_url, params=content_params)
    content_data = content_response.json()

    page_data = content_data["query"]["pages"][str(page_id)]

    result = {
        "title": page_data["title"],
        "extract": page_data["extract"],
        "url": page_data.get("fullurl", f"https://{lang}.wikipedia.org/wiki/{page_data['title'].replace(' ', '_')}"),
    }

    # Add revision information if before date was specified
    if before and "revisions" in page_data:
        revision = page_data["revisions"][0]
        result["revision"] = {
            "id": revision["revid"],
            "timestamp": revision["timestamp"],
            "url": f"https://{lang}.wikipedia.org/w/index.php?oldid={revision['revid']}",
        }

    return result


def print_result(result: dict):
    """Helper function to print search results in a formatted way"""
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print("\n=== Wikipedia Search Result ===")
    print(f"Title: {result['title']}")
    print(f"\nExtract:\n{result['extract']}")
    print(f"\nURL: {result['url']}")
    if "revision" in result:
        print("\nRevision Info:")
        print(f"ID: {result['revision']['id']}")
        print(f"Timestamp: {result['revision']['timestamp']}")
        print(f"Revision URL: {result['revision']['url']}")
    print("============================\n")


if __name__ == "__main__":
    # Test case 1: Basic English search
    print("Test 1: Basic English search")
    result = search_wikipedia("Python programming language")
    print_result(result)

    # Test case 2: Chinese language search
    print("Test 2: Chinese language search")
    result = search_wikipedia("人工智能", lang="zh")
    print_result(result)

    # Test case 3: Search with date
    print("Test 3: Search with historical date")
    result = search_wikipedia("COVID-19", before="2020-03-01")
    print_result(result)

    # Test case 4: Non-existent topic
    print("Test 4: Non-existent topic")
    result = search_wikipedia("xyzabc123nonexistenttopic")
    print_result(result)
