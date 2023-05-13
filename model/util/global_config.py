import json
import os
from attrdict import AttrDict


class GlobalConfig(object):
    _instance = None
    _settings = None

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalConfig, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def _set_config(self, file_name="config.json"):
        _file_path = os.path.join(self.BASE_DIR, 'config', file_name)
        with open(_file_path, 'r') as config_file:
            json_config = json.load(config_file)
            self._instance._settings = AttrDict(json_config)
        assert self._instance._settings.mongo.db is not None
        assert self._instance._settings.mongo.url is not None
        assert self._instance._settings.sources is not None

    def get(self):
        if not self._settings:
            self._set_config()
        return self._settings