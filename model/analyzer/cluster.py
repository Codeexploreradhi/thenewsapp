import nltk
import random
from model.get_logger import get_logger
from model.mlstripper import is_keyword


class Clusterable():
    def __init__(self, sources, num_clusters):
        self.num_clusters = num_clusters
        self.sources = sources
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.clusters = None
        self.vocab_frame = None
        self.terms = None

    @staticmethod
    def _find_one_random_article(articles):
        _articles = filter(lambda a: 'image' in a, articles)
        if _articles and len(_articles) == 1:
            _article = _articles[0]
            return _article['title'], _article['link'], _article['image']
        elif _articles:
            _article = _articles[random.randint(0, len(_articles) - 1)]
            return _article['title'], _article['link'], _article['image']
        else:
            return "", "", ""

    def _get_cluster_terms(self, order_centroids, index, _used_terms):
        get_logger().info("Cluster %d words:" % index)
        _terms = ""
        for ind in order_centroids[index, :8]:
            _term = self.vocab_frame.ix[
                self.terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore')
            if _term not in self.stopwords:
                _terms += " " + _term
        _terms = list(set(filter(lambda term: is_keyword(term), _terms.split())))
        _terms = [t for t in _terms if t not in _used_terms][0:4]
        for t in _terms:
            _used_terms.add(t)
        get_logger().info("%s" % _terms)
        return _terms

    @staticmethod
    def find_polarity(articles):
        return reduce(lambda x, y: x + y,
                      [a.get('polarity', 0) for a in articles]) / len(articles)

    @staticmethod
    def mk_new_cluster(articles, terms, num_of_articles):
        _title, _url, _image = Clusterable._find_one_random_article(articles)
        return {
            "keywords": ", ".join(terms),
            "num_of_articles": num_of_articles,
            "articles": articles,
            "title": _title,
            "url": _url,
            "image":  _image,
            "polarity": Clusterable.find_polarity(articles)
        }
    
    def _get_cluster_titles(self, frame, index, _terms, max_articles=40):
        get_logger().info("Cluster %d titles:" % index)
        _articles = list()
        _titles = frame.ix[index]['title'].values.tolist()
        for title in _titles[0:max_articles]:
            get_logger().info(' %s,' % title)
            _source = self.sources.get(title)
            _article = {"title": title, 'polarity': _source.get('polarity', 0)}
            if _source:
                _article['html'] = _source.get('html', '')
            if _source and _source.get('image'):
                _article['image'] = _source.get('image')
            if _source and _source.get('summary'):
                _article['summary'] = _source.get("summary", '')
            if _source and _source.get('link'):
                _article['link'] = _source.get("link", '')
            if _article.get('html') and _article.get('summary'):
                _articles.append(_article)

        return Clusterable.mk_new_cluster(
            _articles, _terms, len(_titles)
        )
