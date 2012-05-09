import core
from core import *

__all__ = (core.__all__,)

__author__ = 'Prashanth'

VERSION = (0, 0, 1)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    return version

__version__ = get_version()

