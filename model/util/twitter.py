import tweepy
from model.get_logger import get_logger
from . import get_hashtags
from model.util.global_config import GlobalConfig


def post_tweet(topic):
    _hash_tags = get_hashtags(topic['keywords'])
    _config = GlobalConfig().get()
    cfg = {
        "access_token": _config.twitter.access_token,
        "access_secret": _config.twitter.access_secret,
        "consumer_key": _config.twitter.consumer_key,
        "consumer_secret": _config.twitter.consumer_secret,
    }
    try:
        auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
        auth.set_access_token(cfg['access_token'], cfg['access_secret'])
        api = tweepy.API(auth)
        api.update_status(status=topic['url'] + " " + _hash_tags)
    except Exception as e:
        get_logger().error("Error posting to twitter: %s" % e)

