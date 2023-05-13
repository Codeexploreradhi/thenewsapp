import feedparser
from datetime import datetime
from model.get_logger import get_logger
from model.mlstripper import *
from textblob import TextBlob
from time import mktime


def parse_news_article(news_item, source, news_items, news_keywords, max_articles=40):
    _title = clean_hex_and_unicode(strip_tags(news_item.get('title', '')))
    _summary = clean_summary(strip_tags(news_item.get('summary', '')))
    _link = news_item.get('link', '')
    _images = find_images_from_news_item(news_item)
    if not _summary:
        _summary = _title

    if _title and _summary and _link:
        _blob = TextBlob(" ".join(_summary.split("\n"))[0:256])
        _article = {"title": _title, "summary": _summary, "link": _link,
                    "html": news_item['summary'],
                    "source": source, "polarity": _blob.polarity}
        if _images:
            _article["image"] = _images[0]
        news_items.setdefault(_title, _article)
        for _noun in _blob.noun_phrases:
            if news_keywords.get(_noun[:-1]) and _noun.endswith("s"):
                _noun = _noun[:-1]
            if len(_noun.split()) > 1 and "reading" not in _noun:
                _noun_phrase = str(_noun).lower()
                if news_keywords.get(_noun_phrase):
                    if len(news_keywords[_noun_phrase]) < max_articles and \
                        not filter(lambda a: a['title'] == _article['title'],
                                   news_keywords[_noun_phrase]):
                        news_keywords[_noun_phrase].append(_article)
                else:
                    news_keywords[_noun_phrase] = [_article]


def fetch_news_sources(news_sources, max_keywords=15, max_days_elapsed=10):
    news_items = dict()
    news_keywords = dict()
    for _source, _news_sources in news_sources.items():
        for _rss_news_source in _news_sources:
            try:
                get_logger().info("Fetching: %s" % _rss_news_source)
                _feed = feedparser.parse(_rss_news_source)
                for _news_item in _feed['items']:
                    days_elapsed = 0
                    if _news_item.get('published_parsed'):
                        published_time = datetime.fromtimestamp(mktime(_news_item['published_parsed']))
                        days_elapsed = (datetime.now() - published_time).days
                    if days_elapsed <= max_days_elapsed:
                        parse_news_article(_news_item, _source, news_items, news_keywords)
            except Exception as e:
                get_logger().warn("Error reading: %s (%s)" % (_rss_news_source, e))
    get_logger().info("Found %s noun phrases." % len(news_keywords.keys()))
    return news_items, sorted(news_keywords.items(),
                              key=lambda (k, v): (-1 * len(v), k))[0:max_keywords]