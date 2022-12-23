import os
import logging
import json
import tarfile
import StringIO
from collections import OrderedDict
from voidpp_tools.cli_utils import confirm_prompt
from subprocess import check_call, CalledProcessError, PIPE, check_output

from .tool import ToolBase
from .openvpn_config_schema import schema

logger = logging.getLogger(__name__)
cli_handlers = OrderedDict()

def reg_cli_handler(command_name, arguments = [], help = None):
    def decorator(func):
        cli_handlers[command_name] = dict(
            arguments = arguments,
            callback = func,
            help = help,
        )
        return func
    return decorator

class OpenVPNManager(ToolBase):
    name = 'openvpn'
    desc = 'Manage the openvpn clients'

    def register(self, parser):
        subparsers = parser.add_subparsers(dest = 'ovpn_command')

        for command_name, handler in cli_handlers.items():
            subparser = subparsers.add_parser(command_name, help = handler['help'])
            for argument in handler['arguments']:
                subparser.add_argument(*argument['name'], **argument['args'])

    @reg_cli_handler('add-client', [dict(
        name = ['name'],
        args = dict(help = "name of the client"),
    )], 'Generate client certificates and a tar file with the necessary files')
    def add_client(self, name):
        missing_mandatory_files = self.__check_mandatory_files()
        if len(missing_mandatory_files):
            logger.error("Missing mandatory file(s): %s", ', '.join(missing_mandatory_files))
            return

        config = self.__load_config()
        if config is None:
            logger.error("Not found the config file. Please run 'asd openvpn create-config'!")
            return False

        user_file_name = '{}.{}'.format(name, config['server_name'])

        logger.debug("User filename: %s", user_file_name)

        key_name = '{}/{}.key'.format(config['keys_folder'], user_file_name)
        if os.path.exists(key_name):
            logger.error("User '%s' is already exists", name)
            return

        res = self.__generate_client_keys(name)

        if res is False:
            logger.error("Keys were not generated.")
            return

        client_config_data = dict(
            ca = '{}.crt'.format(config['server_name']),
            key = '{}.key'.format(user_file_name),
            cert = '{}.crt'.format(user_file_name),
        )

        filename = self.__create_tar_file(name, client_config_data, config)

        logger.info("Client config created: '%s'", filename)

    def __create_tar_file(self, name, client_config_data, config):
        logger.debug("Create tar file with %s", client_config_data)

        client_ovpn_data = self.__get_client_ovpn_content(config['client_config'], client_config_data)

        ccd = client_config_data

        filename = "{}.{}.tar".format(name, config['server_name'])

        with tarfile.open(filename, 'w') as archive:

            archive.add('{}/ca.crt'.format(config['keys_folder']), ccd['ca'])
            archive.add('{}/{}.crt'.format(config['keys_folder'], name), ccd['cert'])
            archive.add('{}/{}.key'.format(config['keys_folder'], name), ccd['key'])

            client_config_stream = StringIO.StringIO()
            client_config_stream.write(client_ovpn_data)
            client_config_stream.seek(0)

            tarinfo = tarfile.TarInfo(name = '{}.ovpn'.format(config['server_name']))
            tarinfo.size = len(client_config_stream.buf)
            archive.addfile(tarinfo, client_config_stream)

        return filename

    def __check_mandatory_files(self):
        missing_files = []
        for fn in ['vars', 'pkitool']:
            if not os.path.isfile(fn):
                missing_files.append(fn)
        return missing_files

    def __generate_client_keys(self, name):
        command = ['bash', '-c', 'source vars && ./pkitool {}'.format(name)]

        try:
            logger.info(check_output(command, stderr = PIPE))
            return True
        except CalledProcessError as e:
            logger.exception(e)
            return False

    def __load_config(self):
        if not os.path.isfile(self.config_filename):
            return None
        with open(self.config_filename) as f:
            return json.load(f, object_pairs_hook = OrderedDict)

    def __get_client_ovpn_content(self, config_schema, data):
        logger.debug("Generate .ovpn file with data: %s", data)
        lines = []
        for name, value in config_schema.items():
            if name in data:
                value = data[name]
            line = [name]
            if value is not None:
                line += [str(value)]
            lines.append(' '.join(line))

        return '\n'.join(lines)

    @reg_cli_handler('create-config', help = "Create default config. Need to edit the created file!")
    def create_config(self):
        if os.path.exists(self.config_filename):
            logger.error("Config is already exists!")
            if not confirm_prompt("Do you want to override?"):
                return

        with open(self.config_filename, 'w') as f:
            json.dump(schema, f, indent=2)

        logger.info("Config for openvpn manager created: %s", self.config_filename)

    @property
    def config_filename(self):
        return os.path.join(os.getcwd(), 'openvpn-manager.json')

    def process(self, args):
        arg_data = args.__dict__
        command = arg_data['ovpn_command']
        del arg_data['ovpn_command']
        del arg_data['command']
        cli_handlers[command]['callback'](self, **arg_data)
