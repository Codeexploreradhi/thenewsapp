from model.util.global_config import GlobalConfig
from pymongo import TEXT
from pymongo import MongoClient
from bson.son import SON

import re


class NewsDB(object):
    _instance = None
    _client = None
    _db = None
    _topics = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NewsDB, cls).__new__(
                cls, *args, **kwargs)
            _mongo_url = kwargs.get('url', GlobalConfig().get().mongo.url)
            _mongo_db = kwargs.get('db', GlobalConfig().get().mongo.db)
            _client = MongoClient(_mongo_url)
            _db = _client[_mongo_db]
            cls._instance._client = _client
            cls._instance._db = _db
            cls._instance._topics = _db['news_topics']
            cls._instance._keywords = _db['news_keywords']
            cls._instance._cluster_info = _db['cluster_info']
            cls._instance._articles = _db['articles']
        return cls._instance

    def add_news_keywords(self, keywords):
        self._instance._keywords.delete_many({})
        self._instance._keywords.insert_many(keywords)

    def add_news_articles(self, articles):
        _articles = list()
        for _title, _article in articles.items():
            _article['title'] = _title
            # summaries can exceed mongo text index limits.
            _article['summary'] = _article['summary'][0:50]
            _articles.append(_article)
        self._instance._articles.create_index([('title', TEXT), ('summary', TEXT)],
                                              unique=False)
        self._instance._articles.delete_many({})
        self._instance._articles.insert_many(_articles)

    def update_cluster_info(self, cluster_info):
        self._instance._cluster_info.delete_many({})
        self._instance._cluster_info.insert_many([cluster_info])

    def add_topics(self, topics):
        self._instance._topics.delete_many({})
        self._instance._topics.insert_many(topics)

    def fetch_cluster_html(self):
        _clusters = list()
        _cluster_info = {"html": ""}
        for _info in self._instance._cluster_info.find():
            _clusters.append({'html': _info['html']})

        if _clusters:
            _cluster_info = _clusters[0]
        return _cluster_info

    def fetch_cluster_info(self):
        _clusters = list()
        _cluster_info = {"clusters": 0, "words": 0,
                         "articles": 0, "last_update": 0}
        for _info in self._instance._cluster_info.find():
            _clusters.append({'clusters': _info['clusters'],
                              'words': _info['words'],
                              'articles': _info['articles'],
                              'last_update': _info['last_update']})

        if _clusters:
            _cluster_info = _clusters[0]
        return _cluster_info

    @staticmethod
    def _convert_article(a):
        p = re.compile(r'<img.*?/>')
        _html = p.sub('', a['html'])
        return {
            'html': _html,
            'summary': a['summary'],
            'image': a.get('image'),
            'title': a['title'],
            'link': a['link'],
            'polarity': int(a.get('polarity', 0) * 100)
        }

    def _fetch_article_collection(self, collection='news_topics', include_articles=False, convert_keywords=False):
        _topics = list()
        for _topic in self._db[collection].find():
            _keywords = _topic['keywords']
            if convert_keywords:
                _keywords = " ".join(_keywords.split(","))
            _new_topic = {
                'keywords': _keywords,
                'num_of_articles': _topic['num_of_articles'],
                'image': _topic.get('image', "/static/images/no-topic.png"),
                'title': _topic.get('title'),
                'url': _topic.get('url'),
                'polarity': int(_topic.get('polarity', 0) * 100)
            }
            if include_articles:
                _articles = list()
                for a in _topic.get('articles', list()):
                    _articles.append(NewsDB._convert_article(a))
                _new_topic['articles'] = _articles
            _topics.append(_new_topic)

        _topics.sort(key=lambda t: t['num_of_articles'], reverse=True)
        for i, t in enumerate(_topics):
            t['index'] = i
        return _topics

    def fetch_topics(self, include_articles=False):
        return self._instance._fetch_article_collection(include_articles=include_articles)

    def fetch_keywords(self, include_articles=False):
        return self._instance._fetch_article_collection(collection='news_keywords',
                                                        include_articles=include_articles, convert_keywords=True)
    @staticmethod
    def _find_topic_by_id(_topics, topic_id):
        _topic = list(filter(lambda t: str(t['index']) == str(topic_id), _topics))
        if _topic:
            return _topic[0]['keywords'], _topic[0].get('articles', list())
        else:
            return "", list()

    def fetch_articles_by_topic(self, topic_id):
        _topics = self._instance.fetch_topics(include_articles=True)
        return NewsDB._find_topic_by_id(_topics, topic_id)

    def fetch_articles_by_keyword(self, keyword_id):
        _topics = self._instance.fetch_keywords(include_articles=True)
        return NewsDB._find_topic_by_id(_topics, keyword_id)

    def search_articles(self, search_terms, max_articles=40):
        _articles = self._instance._articles.find(
            {"$text": {"$search": "\"" + search_terms + "\""}})[0: max_articles]
        if not _articles:
            _articles = self._instance._articles.find(
                {"$text": {"$search": search_terms}})[0: max_articles]
        return [NewsDB._convert_article(a) for a in _articles]

    def counts_by_source(self):
        _counts_by_source = [["Source", "Articles"]]
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
        ]
        results = list(self._instance._articles.aggregate(pipeline))
        for result in results:
            _counts_by_source.append([result['_id'], result['count']])
        return _counts_by_source