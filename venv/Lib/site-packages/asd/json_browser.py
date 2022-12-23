import sys
import json
import argparse
import logging

from .tool import ToolBase

logger = logging.getLogger(__name__)

class PathSearchException(Exception):
    pass

class InvalidListIndexException(PathSearchException):
    pass

def is_cont(val):
    return type(val) is dict or type(val) is list

class JSONBrowser(ToolBase):
    name = 'json'
    desc = 'Browse json encoded data by keys.'

    def register(self, parser):
        parser.add_argument('infile', nargs = '?', type = argparse.FileType('r'), default = sys.stdin)
        path_action = parser.add_argument('-p', '--path', help = 'path to sub values', default = '')
        parser.add_argument('-k', '--key_list', action = 'store_true')

        path_action.completer = self.get_path_options
        path_action.quoter = self.format_path_options

    def format_path_options(self, completions):
        logger.debug("Formatting completions: %s", completions)
        try:
            if len(completions) == 1:
                if completions[0][-2:-1] == '.':
                    completions[0] = completions[0][:-1]
                return completions
            else:
                comps = []
                for c in completions:
                    cl = c.split('.')
                    comps.append(cl[-1:][0] if len(cl[-1:][0]) else cl[-2:-1][0]+'.')
                return comps
        except Exception as e:
            logger.exception(e)
            return completions

    def get_path_options(self, prefix, parsed_args, action):
        logger.debug("Get keys for prefix '%s'" % prefix)
        try:
            data = json.load(parsed_args.infile)
            path = prefix.split('.')
            (sub_data, keys) = self.get_tree_keys(data, path)
            logger.debug("Found keys: %s" % keys)
            comps = []
            for k in keys:
                comps.append('.'.join(path[:-1] + ['%s.'%k if is_cont(sub_data[k]) else k]))
            logger.debug("Calced completions: %s" % comps)
            return comps
        except Exception as e:
            logger.exception(e)
            return []

    def get_tree_keys(self, data, path):
        if type(data) is dict:
            keys = data.keys()
            if len(path) and path[0] in keys:
                return self.get_tree_keys(data[path[0]], path[1:])
            else:
                return data, keys
        elif type(data) is list:
            idx = int(path[0]) if len(path) and len(path[0]) else -1
            if idx >= 0 and idx < len(data):
                return self.get_tree_keys(data[idx], path[1:])
            else:
                return data, range(len(data))
        return []

    def get_sub_value(self, data, path_array):
        if len(path_array) == 0 or path_array[0] == '':
            return data
        key = path_array.pop(0)
        data_type = type(data)
        if data_type is list:
            if key.isdigit():
                key = int(key)
                if key < 0 or key >= len(data):
                    raise PathSearchException()
            elif key.find(':') != -1:
                sub_keys = key.split(':')
                start_key = sub_keys[0] if len(sub_keys[0]) else 0
                end_key = sub_keys[1] if len(sub_keys[1]) else len(data)
                try:
                    start_key = int(start_key)
                    end_key = int(end_key)
                except ValueError as e:
                    raise InvalidListIndexException()
                return data[start_key:end_key]
            else:
                raise PathSearchException()
        else:
            if key not in data:
                raise PathSearchException()
        return self.get_sub_value(data[key], path_array)

    def process(self, args):
        try:
            data = json.load(args.infile)
            sub_value = self.get_sub_value(data, args.path.split('.'))
            if is_cont(sub_value):
                if args.key_list:
                    if type(sub_value) is dict:
                        print json.dumps(sub_value.keys(), indent = 4)
                    else:
                        print range(len(sub_value))
                else:
                    print json.dumps(sub_value, indent = 4)
            else:
                print sub_value

        except ValueError as e:
            print 'Could not decode json: %s' % e
        except InvalidListIndexException as e:
            print 'Invalid list index: "%s"' % args.path
        except PathSearchException as e:
            print 'Could not find the specified path: "%s"' % args.path


