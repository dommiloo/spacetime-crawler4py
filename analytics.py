import re
from collections import Counter, defaultdict
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
    "at", "by", "for", "from", "in", "into", "of", "on", "to", "with",
    "about", "above", "after", "again", "against", "all", "am", "are",
    "as", "be", "because", "been", "before", "being", "below", "between",
    "both", "can", "did", "do", "does", "doing", "down", "during", "each",
    "few", "further", "had", "has", "have", "having", "he", "her", "here",
    "hers", "herself", "him", "himself", "his", "how", "i", "is", "it",
    "its", "itself", "me", "more", "most", "my", "myself", "no", "nor",
    "not", "now", "off", "once", "only", "other", "our", "ours",
    "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "their", "theirs", "them", "themselves",
    "there", "these", "they", "this", "those", "through", "too", "under",
    "until", "up", "very", "was", "we", "were", "what", "where", "which",
    "while", "who", "whom", "why", "will", "you", "your", "yours"
}

# remove garbage tokens
BAD_WORDS = {"pdf", "html", "http", "https", "www"}


unique_pages = set()
word_counts = Counter()
subdomain_counts = defaultdict(int)

longest_page_url = ""
longest_page_word_count = 0


def record_page(url, html_content):
    global longest_page_url, longest_page_word_count

    clean_url, _ = urldefrag(url)

    if clean_url in unique_pages:
        return

    unique_pages.add(clean_url)

    parsed = urlparse(clean_url)
    subdomain_counts[parsed.netloc.lower()] += 1

    soup = BeautifulSoup(html_content, "html.parser")

    # remove junk tags
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator=" ")
    words = re.findall(r"[a-zA-Z]+", text.lower())

    filtered_words = [
        word for word in words
        if word not in STOP_WORDS
        and word not in BAD_WORDS
        and len(word) > 1
    ]

    word_counts.update(filtered_words)

    if len(words) > longest_page_word_count:
        longest_page_word_count = len(words)
        longest_page_url = clean_url


def write_report(filename="crawler_report.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("1. Unique pages found:\n")
        f.write(f"{len(unique_pages)}\n\n")

        f.write("2. Longest page by word count:\n")
        f.write(f"{longest_page_url}, {longest_page_word_count} words\n\n")

        f.write("3. Top 50 words:\n")
        for word, count in word_counts.most_common(50):
            f.write(f"{word}, {count}\n")

        f.write("\n4. Subdomains:\n")
        for subdomain in sorted(subdomain_counts):
            f.write(f"{subdomain}, {subdomain_counts[subdomain]}\n")