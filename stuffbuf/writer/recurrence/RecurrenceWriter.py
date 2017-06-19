from collections import deque
import logging

from stuffbuf.writer.Source import Source
from stuffbuf.parse.ztransform import ZTransformParser


class RecurrenceSession:

    def __init__(self, exp, init, limit, memdepth, *args, **kwargs):
        self.exp = exp
        self.init = init
        self.limit = limit

        self.bytedepth = 2
        self.memdepth = memdepth
        self.mod_mask = 0xFFFF

    def run(self):
        reg = self.init
        memory = deque([0] * self.memdepth, self.memdepth)
        for _ in range(self.limit):
            yield (reg & self.mod_mask).to_bytes(
                self.bytedepth, byteorder='big'
            )
            memory.append(reg & self.mod_mask)
            reg = self.exp(memory)


class RecurrenceWriter(Source):

    @classmethod
    def fmt(cls):
        return 'rec'

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        exp = ZTransformParser().parse(args_dict.get('exp', 'w**2 + w'))
        memdepth = int(args_dict.get('memdepth', '16'))
        init = int(args_dict.get('init', '0xffff'), 16)
        limit = int(args_dict.get('limit', '88200'))

        return dict(
            exp=exp,
            init=init,
            limit=limit,
            memdepth=memdepth
        )

    def create_session(self, *args, **kwargs):
        return RecurrenceSession(*args, **kwargs)

    def generate(self, *args, **kwargs):
        session = self.create_session(*args, **kwargs)
        return session.run()
