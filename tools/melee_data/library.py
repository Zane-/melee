#!/usr/bin/env python3
"""Parse The Melee Library (https://www.meleelibrary.com/, one page of link
cards grouped by section) into data/resources/meleelibrary.json.

    python tools/melee_data/library.py [--html saved_page.html] [--out FILE]

Output: a list of sections {level, id, title, description, cards}, each card
{title, url, author, description, links}. render.py turns it into markdown.
"""
import argparse
import json
import os
import re
import urllib.request
from html.parser import HTMLParser

URL = "https://www.meleelibrary.com/"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections = []   # {title,id,level,description,cards:[]}
        self.stack = []      # (tag, class)
        self.card = None
        self.cap = None      # current capture target key
        self.buf = []
        self.links = []
        self.h = None
    def cls_in(self, c):
        return any(c in (k or '') for _, k in self.stack)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('br', 'img', 'meta', 'link', 'hr', 'input'):
            return
        c = a.get('class', '')
        self.stack.append((tag, c))
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self.h = {'level': int(tag[1]), 'id': a.get('id', ''), 'title': ''}
            self.buf = []
        elif 'card' == c.strip():
            self.card = {'title': '', 'url': '', 'author': '', 'description': '', 'links': []}
        elif c.strip() in ('card-title', 'card-author', 'card-description', 'topic-description'):
            self.cap = c.strip(); self.buf = []; self.caplevel = len(self.stack)
        if tag == 'a' and a.get('href'):
            href = a['href']
            if self.cap == 'card-title' and self.card is not None and not self.card['url']:
                self.card['url'] = href
            elif self.card is not None and self.cap:
                self.card['links'].append(href)
                self.buf.append('[')
                self._pending = href
            elif self.cap == 'topic-description':
                self.buf.append('['); self._pending = href
    def handle_endtag(self, tag):
        if tag in ('br', 'img'):
            return
        if tag == 'a' and getattr(self, '_pending', None):
            self.buf.append('](%s)' % self._pending); self._pending = None
        if self.h is not None and tag == 'h%d' % self.h['level']:
            self.h['title'] = ' '.join(''.join(self.buf).split())
            self.sections.append(dict(self.h, description='', cards=[]))
            self.h = None; self.buf = []
        if self.cap and len(self.stack) == self.caplevel:
            text = ' '.join(''.join(self.buf).split())
            if self.cap == 'topic-description':
                if self.sections: self.sections[-1]['description'] = text
            elif self.card is not None:
                key = self.cap[5:]
                if key == 'author': text = re.sub(r'^by\s+', '', text)
                self.card[key] = text
            self.cap = None; self.buf = []
        # close
        while self.stack:
            t, c = self.stack.pop()
            if c.strip() == 'card' and self.card is not None:
                if self.sections and (self.card['title'] or self.card['url']):
                    self.sections[-1]['cards'].append(self.card)
                self.card = None
            if t == tag: break
    def handle_data(self, d):
        if self.h is not None or self.cap:
            self.buf.append(d)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--html", help="parse a saved copy instead of fetching")
    ap.add_argument("--out", default=os.path.join(
        REPO, "data", "resources", "meleelibrary.json"))
    args = ap.parse_args()
    if args.html:
        with open(args.html, encoding="utf-8") as f:
            page = f.read()
    else:
        req = urllib.request.Request(URL, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) melee-data"})
        with urllib.request.urlopen(req, timeout=60) as r:
            page = r.read().decode("utf-8")
    page = page[page.find("<main>"):]
    p = P()
    p.feed(page)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(p.sections, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("%d sections, %d cards -> %s" % (
        len(p.sections), sum(len(x["cards"]) for x in p.sections),
        os.path.relpath(args.out, REPO)))


if __name__ == "__main__":
    main()
