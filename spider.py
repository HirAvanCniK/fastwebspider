#!/usr/bin/python3

import requests, os, sys, threading
from bs4 import BeautifulSoup

class Spider():
    BLACKLIST = []
    FOUND = False

    def __init__(self, base_url: str, term_to_find: str, threads=True, block_on_found=False):
        self.BASE_URL = base_url
        self.TERM_TO_FIND = term_to_find
        self.THREADS = threads
        self.BLOCK_ON_FOUND = block_on_found

    def find_term(self, txt: str, page: str):
        if self.TERM_TO_FIND in txt:
            for line in txt.splitlines():
                if self.TERM_TO_FIND in line:
                    print(f"Found in {page}:", line.strip())
                    if self.BLOCK_ON_FOUND:
                        self.FOUND = True
                        exit()

    def visit(self, url: str) -> list:
        r = requests.get(url)
        self.find_term(r.text, r.url)
        ctx = BeautifulSoup(r.text, features='html.parser')
        links = ctx.findAll("a")
        return [link.get('href') for link in links if link.get('href') not in self.BLACKLIST and link.get('href').startswith("/")]

    def spider(self, url: str):
        if not self.FOUND:
            new_pages = self.visit(url)
            self.BLACKLIST += new_pages
            for page in new_pages[::-1]:
                if self.THREADS:
                    threading.Thread(target=self.spider, args=(self.BASE_URL+page,)).start()
                else:
                    self.spider(self.BASE_URL+page)

    def start(self):
        print(f"Searching '{self.TERM_TO_FIND}' on {self.BASE_URL}...")
        self.spider(self.BASE_URL)

def show_help():
    print(f"""\
🕷️ Welcome to the Web Spider Tool! 🕷️

This script allows you to search for a specific term on a website and optionally crawl its links.

HOW TO USE:
  python3 {os.path.basename(__file__)} -H <HOST> -t <TERM_TO_FIND> [options]

MANDATORY PARAMETERS:
  -H <HOST>           The base URL of the website to crawl. (e.g., https://example.com)
  -t <TERM_TO_FIND>   The term or keyword you want to search for on the website.

OPTIONS:
  -nT                 Disable multi-threading (default: threading enabled).
  -s                  Stop crawling immediately when the term is found.
  -h                  Show this help message and exit.

EXAMPLES:
  1. Search for the term "privacy" on example.com:
     python spider.py -H https://example.com -t privacy

  2. Search for "cookie" without multi-threading:
     python spider.py -H https://example.com -t cookie -nT

  3. Search for "contact" and stop immediately when found:
     python spider.py -H https://example.com -t contact -s

🕸️ Enjoy your spidering journey! 🕸️""")

def get_args() -> dict:
    flags_with_argument = ['H', 't']
    flags_without_argument = ['h', 'nT', 's']
    return_dict = {}
    for flag in flags_without_argument:
        if "-"+flag in sys.argv:
            sys.argv.pop(sys.argv.index("-"+flag))
            match flag:
                case 'h':
                    show_help()
                    exit()
                    break
                case 'nT':
                    return_dict['nT'] = False
                    break
                case 's':
                    return_dict['s'] = True
                    break
    
    if "nT" not in return_dict:
        return_dict['nT'] = True
    if "s" not in return_dict:
        return_dict['s'] = False

    for i, flag in enumerate(sys.argv):
        if flag.startswith("-"):
            if flag[1:] in flags_with_argument:
                try:
                    return_dict[flag[1:]] = sys.argv[i+1]
                except:
                    print(f"Flag '{flag}' needs an argument!")
                    exit()
            else:
                print(f"Unkown flag found '{flag}'!")
                exit()
    return return_dict

if __name__ == "__main__":
    args = get_args()
    if not args.get('H') or not args.get('t'):
        show_help()
        exit()
    if args.get('H').endswith("/"):
        args['H'] = args['H'][:-1]
    Spider(args.get('H'), args.get('t'), args.get('nT'), args.get('s')).start()
