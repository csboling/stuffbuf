from abc import abstractmethod
from functools import reduce
from io import BytesIO

from stuffbuf.writer.Writer import Writer
from stuffbuf import xform


def identity(*xs):
    return lambda x: x


class CombinatorWriter:

    def __init__(self, comb, *args):
        self.combinator = comb
        self.args = args

    def write(self, source, target, func_name='', *args):
        action = getattr(xform, func_name, identity)
        f = action(*args)
        buf = bytes(self.combinator(f, source.read(), *self.args))
        print('writing {} bytes'.format(len(buf)))
        target.write(buf)


class MapWriter(Writer):

    def __init__(self):
        self.cw = CombinatorWriter(map)

    @classmethod
    def fmt(cls):
        return 'map'

    def write(self, *args, **kwargs):
        self.cw.write(*args, **kwargs)


class ReduceWriter(Writer):

    def __init__(self):
        self.cw = CombinatorWriter(reduce, b'')

    @classmethod
    def fmt(cls):
        return 'reduce'

    def write(self, *args, **kwargs):
        self.cw.write(*args, **kwargs)


class SortWriter(Writer):

    def __init__(self):
        self.cw = CombinatorWriter(lambda f, it: iter(sorted(it)))

    @classmethod
    def fmt(cls):
        return 'sort'

    def write(self, *args, **kwargs):
        self.cw.write(*args, **kwargs)
