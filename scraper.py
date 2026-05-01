import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from analytics import record_page, write_report


ALLOWED_DOMAINS = {
    "ics.uci.edu",
    "cs.uci.edu",
    "informatics.uci.edu",
    "stat.uci.edu"
}


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    output_links = []

    if resp is None:
        return output_links

    if resp.status != 200:
        return output_links

    if resp.raw_response is None or resp.raw_response.content is None:
        return output_links

    try:
        # record stats
        record_page(url, resp.raw_response.content)
        write_report()

        soup = BeautifulSoup(resp.raw_response.content, "html.parser")

        for tag in soup.find_all("a", href=True):
            href = tag["href"]

            absolute_url = urljoin(url, href)
            clean_url, _ = urldefrag(absolute_url)

            output_links.append(clean_url)

    except Exception as e:
        print("Error parsing page:", url, e)

    return list(set(output_links))


def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        domain = parsed.netloc.lower()

        # restrict to allowed domains
        if not any(domain == allowed or domain.endswith("." + allowed)
                   for allowed in ALLOWED_DOMAINS):
            return False

        path = parsed.path.lower()

        # block non-html files
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            path
        ):
            return False

        lowered = url.lower()

        # avoid traps
        trap_words = [
            "calendar",
            "ical",
            "wp-json",
            "replytocom",
            "share=",
            "sort=",
            "filter=",
            "sessionid",
            "sid=",
        ]

        if any(word in lowered for word in trap_words):
            return False

        # avoid too many query params
        if "?" in url and url.count("=") > 2:
            return False

        # avoid deep/repetitive paths
        parts = [p for p in path.split("/") if p]

        if len(parts) > 12:
            return False

        for part in set(parts):
            if parts.count(part) > 3:
                return False

        return True

    except TypeError:
        print("TypeError for", url)
        return False