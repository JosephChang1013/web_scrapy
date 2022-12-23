import os
from voidpp_tools.json_config import JSONConfigLoader, ConfigLoaderException

loader = JSONConfigLoader(__file__)

def load_config():
    return loader.load('asd-config.json', create = os.path.expanduser('~'))

def save_config(config):
    loader.save(config)
