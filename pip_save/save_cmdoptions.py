from functools import partial
from optparse import Option

save = partial(
    Option,
    '--save',
    dest='save',
    action='store_true',
    help='Save requirement as a dependency to the metadata file.'
)

save_dev = partial(
    Option,
    '--save-dev',
    dest='save_dev',
    action='store_true',
    help='Save requirement as a development dependency to the metadata file.'
)
