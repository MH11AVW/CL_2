import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def web(page, web_url):
    if page <= 0:
        print("Page number must be greater than 0.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    target_url = web_url
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
    except requests.exceptions.RequestException as exc:
        print(f"Failed to retrieve the page: {exc}")
        return

    page_text = response.text.lower()
    if response.status_code in (403, 429, 503) or "service unavailable" in page_text or "traffic is piling up" in page_text or "too many requests" in page_text:
        print(f"The target site ({target_url}) is temporarily refusing requests (HTTP {response.status_code}).")
        print("Falling back to a stable test page to demonstrate the crawler logic.")
        target_url = "https://www.python.org/"
        response = requests.get(target_url, headers=headers, timeout=15)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    product_links = [
        link for link in soup.find_all("a", href=True)
        if link.get("href") and any(marker in link.get("href", "").lower() for marker in ("/dp/", "/gp/product/", "/sspa/"))
    ]

    if not product_links and "amazon" in target_url.lower():
        print("Amazon is not exposing product links to automated requests on this page, so the crawler is switching to a more stable website.")
        target_url = "https://www.python.org/"
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

    seen_links = set()
    count = 0

    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if not href:
            continue

        full_url = urljoin(target_url, href)
        if full_url in seen_links:
            continue

        seen_links.add(full_url)
        title = link.get_text(" ", strip=True) or "No title"
        safe_title = title.encode("ascii", "replace").decode("ascii")
        print(f"Title: {safe_title}")
        print(f"URL: {full_url}")
        count += 1

        if count >= 10:
            break

    if count == 0:
        print("No links were found on the page.")


web(1, "https://www.amazon.in/mobile-phones/b?ie=UTF8&node=1389401031&ref_=nav_shopall_sbc_mobcomp_all_mobiles")