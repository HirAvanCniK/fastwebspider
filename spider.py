import requests, os, sys, threading
from bs4 import BeautifulSoup

BLACKLIST = []
FOUND = False

def find_term(txt, page):
    if TERM_TO_FIND in txt:
        for line in txt.splitlines():
            if TERM_TO_FIND in line:
                print(f"Found in {page}:", line.strip())
                if len(sys.argv) == 4:
                    global FOUND
                    FOUND = True
                    exit()

def visit(url):
    r = requests.get(url)
    find_term(r.text, r.url)
    ctx = BeautifulSoup(r.text, features='html.parser')
    links = ctx.findAll("a")
    return [link.get('href') for link in links if link.get('href') not in BLACKLIST and link.get('href').startswith("/")]

def spider(url):
    global FOUND
    if not FOUND:
        new_pages = visit(url)
        global BLACKLIST
        BLACKLIST += new_pages
        for page in new_pages[::-1]:
            t = threading.Thread(target=spider, args=(BASE_URL+page,))
            t.start()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {os.path.basename(__file__)} <HOST> <TERM_TO_FIND> [<STOPONFOUND>]")
        exit()
    BASE_URL = sys.argv[1]
    if BASE_URL.endswith("/"):
        BASE_URL = BASE_URL[:-1]
    TERM_TO_FIND = sys.argv[2]
    print(f"Searching '{TERM_TO_FIND}' on {BASE_URL}...")
    spider(BASE_URL)
