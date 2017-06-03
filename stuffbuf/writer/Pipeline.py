from functools import reduce
import operator

import stuffbuf.writer as writer


class Pipeline:

    def __init__(self, src):
        stages = list(map(self.parse, src.split('|')))

        self.source = False
        if len(stages):
            if isinstance(stages[0], writer.Source):
                self.source = True
            self.writer = reduce(operator.__or__, stages)
        else:
            self.writer = writer.IdWriter()

    def parse(self, stage):
        writer_type, *args = stage.split()
        w = writer.Writer.create(writer_type)
        w.bind_args(*args)
        return w

    def write(self, *args, **kwargs):
        self.writer.write(*args, **kwargs)
