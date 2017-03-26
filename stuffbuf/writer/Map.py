from stuffbuf.writer.Writer import Writer
from stuffbuf import xform


class MapWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'map'

    @staticmethod
    def identity(x, *xs):
        return x

    def write(self, source, target, func_name, *args):
        action = getattr(xform, func_name, self.identity)
        f = action(*args)
        buf = bytes(map(f, source.read()))
        print(len(buf))
        target.write(buf)
