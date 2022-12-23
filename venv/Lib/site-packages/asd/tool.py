
import sys
import inspect
import importlib
import logging
from abc import ABCMeta, abstractmethod
from .system_config import load_config, save_config

logger = logging.getLogger(__name__)

class ToolBase(object):
    __metaclass__ = ABCMeta

    name = None
    desc = None
    example_config = {}

    def __init__(self, config = {}):
        self.config = config

    @abstractmethod
    def register(self, parser):
        pass

    @abstractmethod
    def process(self, args):
        pass

class ToolHelper():

    @staticmethod
    def _get_tool_classes(name):
        external_module = importlib.import_module(name)
        for type_name, type in inspect.getmembers(external_module):
            if inspect.isclass(type) and type is not ToolBase and ToolBase in inspect.getmro(type):
                yield type

    @staticmethod
    def register_external_tools_module(name):
        config = load_config('/etc')
        if 'external_tools' not in config:
            config['external_tools'] = dict()
        config['external_tools'][name] = {}
        for type in ToolHelper._get_tool_classes(name):
            if type.name not in config['external_tools'][name]:
                config['external_tools'][name][type.name] = dict(
                    enabled = True,
                    config = type.example_config,
                )
        save_config(config)

    @staticmethod
    def load_external_tools(system_config, user_config):
        tools = []
        undefined_tools = []
        for name in system_config:
            for type in ToolHelper._get_tool_classes(name):
                cfg = system_config[name].get(type.name)
                if cfg is None and name not in undefined_tools:
                    undefined_tools.append(name)
                    continue
                if name in user_config and type.name in user_config[name]:
                    cfg = user_config[name][type.name]
                if cfg['enabled']:
                    tools.append(type(cfg['config']))

        if len(undefined_tools):
            logger.error("There are undefined tool(s) in these package(s): %s. Exec 'asd register <package_name>' with the necessary permission.", ', '.join(undefined_tools))

        return tools
