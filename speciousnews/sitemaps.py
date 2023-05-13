from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from newsfeed.news_db import NewsDB


class SpeciousNewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        _keywords = NewsDB().fetch_keywords()
        for _k in _keywords:
            _k['is_keyword'] = True
        _topics = NewsDB().fetch_topics()
        for _t in _topics:
            _t['is_keyword'] = False
        _topics.extend(_keywords)
        return _topics

    def location(self, item):
        if item.get('is_keyword', False):
            return reverse('news_keywords', kwargs={'keyword_id': item['index']})
        else:
            return reverse('news_topics', kwargs={'topic_id': item['index']})
