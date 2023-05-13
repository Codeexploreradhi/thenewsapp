import facebook
from model.get_logger import get_logger
from . import get_hashtags
from model.util.global_config import GlobalConfig


def post_message(topic):
    _hash_tags = get_hashtags(topic['keywords'])
    _config = GlobalConfig().get()
    cfg = {
        "page_id": _config.facebook.page_id,
        "access_token": _config.facebook.access_token
    }
    attachment = {
        "link": topic['url'],
        'caption': "http://www.speciousnews.com"
    }
    try:
        api = facebook.GraphAPI(cfg["access_token"])
        api.put_wall_post(message=topic['title'] + " " + _hash_tags,
                          attachment=attachment, profile_id=cfg['page_id'])
    except Exception as e:
        get_logger().error("Error posting to facebook: %s" % e)

