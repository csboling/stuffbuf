from functools import reduce
import operator

import stuffbuf.writer as writer


class Pipeline:

    def __init__(self, src):
        self.writer = reduce(
            operator.__or__,
            map(self.parse, src.split('|')),
            writer.IdWriter()
        )

    def parse(self, stage):
        writer_type, *args = stage.split()
        w = writer.Writer.create(writer_type)
        w.bind_args(*args)
        return w

    def write(self, *args, **kwargs):
        self.writer.write(*args, **kwargs)
