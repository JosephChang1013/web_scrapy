import sys
import json
import argparse
import logging

from .tool import ToolBase, ToolHelper

logger = logging.getLogger(__name__)

class Register(ToolBase):
    name = 'register'
    desc = 'Register external asd tools package'

    def register(self, parser):
        parser.add_argument('name', help = 'The name of the python package')

    def process(self, args):
        ToolHelper.register_external_tools_module(args.name)
        print 'Tools registered successfully'
