
from voidpp_tools.json_config import JSONConfigLoader
from voidpp_tools.config_loader import ConfigFileNotFoundException

loader = JSONConfigLoader(__file__)

def load_config(create = None):
    try:
        config = loader.load('asd-system-config.json', create = create)
    except ConfigFileNotFoundException:
        config = {}
    return config

def save_config(config):
    loader.save(config)
