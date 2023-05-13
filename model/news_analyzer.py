import pandas as pd
import mpld3
import time

import matplotlib.pyplot as plt
from analyzer.cluster import Clusterable
from analyzer.tokenizer import Tokenizable
from d3_helper import TopToolbar
from model.get_logger import get_logger
from nltk.stem.snowball import SnowballStemmer
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class NewsAnalyzer(Clusterable, Tokenizable):
    def __init__(self, news_items, num_clusters=12,
                 output_file="doc_cluster.pkl"):
        self.summaries = map(lambda i: i['summary'], news_items.values())
        self.titles = news_items.keys()
        self.output_file = output_file
        self.topics = list()
        self.dist = None
        Clusterable.__init__(self, news_items, num_clusters)
        Tokenizable.__init__(self, SnowballStemmer("english"))

    def tfidf_maxtrix(self):
        get_logger().info("Generating TfDif vector.")
        vectorizer = TfidfVectorizer(max_df=0.5, max_features=2**20,
                                     min_df=0.005, stop_words='english',
                                     use_idf=True, tokenizer=self.tokenize_and_stem,
                                     ngram_range=(1, 3))
        get_logger().info("Fitting TfDif vector.")
        tfidf_matrix = vectorizer.fit_transform(self.summaries)
        get_logger().info(tfidf_matrix.shape)
        self.terms = vectorizer.get_feature_names()
        get_logger().info("Calculating similarity between documents")
        self.dist = 1 - cosine_similarity(tfidf_matrix)
        return tfidf_matrix

    def k_means(self):
        for i in self.summaries:
            self.totalvocab_stemmed.extend(
                self.tokenize_and_stem(i))
            self.totalvocab_tokenized.extend(
                Tokenizable.tokenize_only(i))
        self.vocab_frame = pd.DataFrame({'words': self.totalvocab_tokenized}, index=self.totalvocab_stemmed)
        get_logger().info("There are %s items in vocab_frame" % str(self.vocab_frame.shape[0]))
        km = KMeans(n_clusters=self.num_clusters)
        km.fit(self.tfidf_maxtrix())
        joblib.dump(km, self.output_file)
        return {
            "clusters": self.num_clusters,
            "words": int(str(self.vocab_frame.shape[0])),
            "articles": len(self.titles),
            "last_update": int(time.time()),
        }

    @staticmethod
    def analyze_keywords(keywords):
        _keywords = list()
        for _keyword, _articles in keywords:
            _keywords.append(
                Clusterable.mk_new_cluster(
                    _articles, _keyword.split(), len(_articles)
                )
            )
        return _keywords

    def analyze(self):
        km = joblib.load(self.output_file)
        clusters = km.labels_.tolist()
        self.clusters = clusters
        _news_items = {'title': self.titles, 'synopsis': self.summaries, 'cluster': clusters}
        frame = pd.DataFrame(_news_items, index=[clusters], columns=['title', 'cluster'])
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        _topics = list()
        _used_terms = set()

        for i in range(self.num_clusters):
            _terms = self._get_cluster_terms(order_centroids, i, _used_terms)
            _topic = self._get_cluster_titles(frame, i, _terms)
            _topics.append(_topic)
        self.topics = _topics
        return _topics

    def view_cluster_html(self):
        pca = TruncatedSVD(100)
        pos = pca.fit_transform(self.dist)
        
        xs, ys = pos[:, 0], pos[:, 1]
        cluster_names = {i: t['keywords'] for i, t in enumerate(self.topics)}
        df = pd.DataFrame(dict(x=xs, y=ys, label=self.clusters, title=self.titles))
        groups = df.groupby('label')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.margins(0.03)

        for name, group in groups:
            points = ax.plot(group.x, group.y, marker='o', linestyle='', ms=18,
                             label=cluster_names[name], mec='none',
                             color=TopToolbar.CLUSTER_COLORS[name])
            ax.set_aspect('auto')
            labels = [i for i in group.title]
            tooltip = mpld3.plugins.PointHTMLTooltip(points[0], labels, voffset=10,
                                                     hoffset=10, css=TopToolbar.CSS)
            mpld3.plugins.connect(fig, tooltip, TopToolbar())
            ax.axes.get_xaxis().set_ticks([])
            ax.axes.get_yaxis().set_ticks([])
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
        ax.legend(numpoints=1)
        return mpld3.fig_to_html(fig)



