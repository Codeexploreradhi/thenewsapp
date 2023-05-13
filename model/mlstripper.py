import re
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def is_keyword(term):
    return term and len(term) > 3 and term[0].isalpha()


def find_images_in_markup(html):
    _image_tags = list()
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")
    for img in img_tags:
        _img_src = img.get("src")
        if _img_src and not _img_src.startswith("http://feeds.feedburner.com"):
            _image_tags.append(_img_src)
    return _image_tags


def find_images_from_news_item(news_item):
    _image_tags = list()
    media_items = news_item.get('media_content', list())
    for _mitem in media_items:
        if _mitem.get('url'):
            _image_tags.append(_mitem['url'])
    if not _image_tags:
        _image_tags = find_images_in_markup(news_item.get('summary', ''))
    return _image_tags


def clean_hex_and_unicode(raw):
    raw = re.sub(r"[^\x00-\x7F]+", "", raw)
    return str(raw.decode('unicode_escape').encode('ascii', 'ignore'))


def strip_phrases(raw):
    phrases = ["The post ", "appeared first on The Intercept.", "Read Full Article at RT.com"]
    for phrase in phrases:
        raw = raw.replace(phrase, "")
    return raw


def clean_summary(summary):
    _common_words = ["continue", "reading", "read", "more", "says", "said"]
    return " ".join(
        filter(
            lambda s: is_keyword(s) and s.lower() not in _common_words, summary.split()))


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    _raw = s.get_data().strip()
    return strip_phrases(clean_hex_and_unicode(_raw))
