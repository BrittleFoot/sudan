"""
    Common functions and tools
"""


def deeplen(iterable):
    return sum(map(len, iterable.values()))


class IOWrapper:
    """ wraps iterator with io buffer - like methods
    Handy to use with GFF parser if you do not have IO buffer.
    """

    def __init__(self, obj):
        self._iter = obj

    def read(self):
        pass

    def readline(self):
        try:
            return next(self._iter)
        except StopIteration:
            return ""

    def close(self):
        pass
