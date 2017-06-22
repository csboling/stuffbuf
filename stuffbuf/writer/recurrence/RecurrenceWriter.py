import ast
from collections import deque
import logging
import struct

from sympy import re, sympify

from stuffbuf.writer.Source import Source
from stuffbuf.parse.ztransform import ZTransformParser
from stuffbuf.parse.recurrence import RecurrenceParser


class RecurrenceSession:

    def __init__(self, exp, init, limit, memdepth, bytedepth, *args, **kwargs):
        self.exp = exp
        self.init = init
        self.limit = limit

        self.bytedepth = bytedepth
        self.memdepth = memdepth
        self.mod_mask = 2**(8 * self.bytedepth) - 1
        logging.info('depth {}, mask {}'.format(self.bytedepth, self.mod_mask))

    def condition(self, memory):
        return [float(re(sympify(x))) for x in memory]

    def gain(self):
        return self.mod_mask // 2

    def run(self):
        memory = deque(self.condition(self.init), self.memdepth)
        half_scale = self.mod_mask // 2
        for _ in range(self.limit):
            y = self.exp(memory)
            sample = (int(y) & self.mod_mask) - half_scale
            logging.debug(
                (
                    '{:0' + str(self.bytedepth * 2) + 'x}'
                    +
                    ' <- {} = step({})'
                ).format(sample, y, list(memory))
            )
            yield sample.to_bytes(
                self.bytedepth,
                byteorder='little',
                signed=True
            )
            memory.append(y)


class RecurrenceWriter(Source):

    @classmethod
    def fmt(cls):
        return 'rec'

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        memdepth = int(args_dict.get('memdepth', '16'))
        # exp = ZTransformParser().parse(
        #     args_dict.get('exp', 'z**-2 + z**-1'),
        #     depth=memdepth
        # )
        rec = RecurrenceParser().parse(
            args_dict.get('rec', 'x(n-1) + x(n-2)'),
            depth=memdepth
        )
        init = ast.literal_eval(args_dict.get('init', str([0] * 16)))
        limit = int(args_dict.get('limit', '88200'))
        bytedepth = int(args_dict.get('bytedepth', '4'))

        return dict(
            # exp=exp,
            exp=rec,
            init=init,
            limit=limit,
            memdepth=memdepth,
            bytedepth=bytedepth
        )

    def create_session(self, *args, **kwargs):
        return RecurrenceSession(*args, **kwargs)

    def generate(self, *args, **kwargs):
        session = self.create_session(*args, **kwargs)
        return session.run()
