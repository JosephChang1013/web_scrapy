import re
from setuptools.command.install import install as install_base
from asd.tool import ToolHelper

# Note that I use the class name 'install' for the derived class because that is what python setup.py --help-commands will use.
class install(install_base):
    def run(self):
        install_base.run(self)

        # search for the package name for auto register
        installed_files = self.get_outputs()
        pkg_name = None
        # yes, this is a little bit hacky, but I did not found any other way...
        for file in installed_files:
            matches = re.search('dist\-packages\/(.*)\/__init__\.pyc', file)
            if matches:
                pkg_name = matches.group(1)
                break

        if pkg_name is None:
            self.warn('Package name not found. Auto register is not possible.')
            return

        ToolHelper.register_external_tools_module(pkg_name)
