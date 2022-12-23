from collections import OrderedDict
from subprocess import check_output

schema = dict(
    server_name = check_output(['hostname']).strip(),
    keys_folder = 'keys',
    client_config = OrderedDict([
        ('client', None),
        ('dev', 'tun'),
        ('proto', 'udp'),
        ('remote', None),
        ('resolv-retry', 'infinite'),
        ('nobind', None),
        ('user', 'nobody'),
        ('group', 'nogroup'),
        ('persist-key', None),
        ('persist-tun', None),
        ('ca', None),
        ('cert', None),
        ('key', None),
        ('ns-cert-type', 'server'),
        ('comp-lzo', None),
        ('verb', 3),
    ]),
)
