import json
import os
import pickle
import random
import sys

from model.get_logger import get_logger
from model.news_analyzer import NewsAnalyzer
from model.news_parser import fetch_news_sources
from model.util.fb import post_message
from model.util.twitter import post_tweet
from model.util.global_config import GlobalConfig
from newsfeed.news_db import NewsDB


def load_config(config_file):
    try:
        with open(config_file, "r") as config_file_data:
            _config_file_settings = json.load(config_file_data)
        return _config_file_settings
    except Exception as e:
        get_logger().error("Error opening config file: %s" % e)
        return None


def check_config(config_settings):
    if not config_settings:
        get_logger().error("Invalid config file.  Exiting...\n");
        sys.exit(0)


def safe_delete(filename):
    try:
        os.remove(filename)
    except Exception as e:
        return e


def load_model():
    _config_settings = load_config(os.path.join("config", GlobalConfig().get().sources))
    check_config(_config_settings)
    _feeds = _config_settings['news']['sources']
    _news_sources, _keywords = fetch_news_sources(_feeds)
    safe_delete('news_sources.pkl')
    safe_delete('news_keywords.pkl')
    with open('news_sources.pkl', 'w') as outfile:
        pickle.dump(_news_sources, outfile)
    with open('news_keywords.pkl', 'w') as outfile:
        pickle.dump(_keywords, outfile)
    get_logger().info(
        "Fetched %s news articles from %s sources..." % (len(_news_sources.keys()), len(_feeds)))


def find_one_random_topic(topics):
    return topics[random.randint(0, len(topics) - 1)]


def run_model():
    with open("news_sources.pkl", "r") as news_sources_file:
            _news_sources = pickle.loads(news_sources_file.read())
    with open("news_keywords.pkl", "r") as news_keywords_file:
            _keywords = pickle.loads(news_keywords_file.read())
    safe_delete('doc_cluster.pkl')
    try:
        news = NewsAnalyzer(news_items=_news_sources)
        _cluster_info = news.k_means()
        _topics = news.analyze()
        get_logger().info("Storing results to mongo db...")
        NewsDB().add_topics(_topics)
        get_logger().info("Finished saving results to mongo db...")
        get_logger().info("Saving cluster graph file as html.")
        _cluster_info['html'] = news.view_cluster_html()
        NewsDB().update_cluster_info(_cluster_info)
        get_logger().info("Saved cluster graph to html.")
        get_logger().info("Saving news articles.")
        NewsDB().add_news_articles(_news_sources)
        get_logger().info("Analyzing and saving keywords.")
        _keywords = NewsAnalyzer.analyze_keywords(_keywords)
        NewsDB().add_news_keywords(_keywords)
        get_logger().info("Posting link(s) to social media.")
        post_message(find_one_random_topic(_topics + _keywords))
        post_tweet(find_one_random_topic(_topics + _keywords))
        get_logger().info("Done.")
    except Exception as e:
        get_logger().error("Error running model: %s" % str(e))


def show_usage():
    print("Usage: python news.py [--load | --run]\n")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        show_usage()
    get_logger().info("Starting news model...")

    if len(sys.argv) == 1:
        load_model()
        run_model()
    elif sys.argv[1].lower() == "--load":
        load_model()
    elif sys.argv[1].lower() == "--run":
        run_model()
    else:
        show_usage()
