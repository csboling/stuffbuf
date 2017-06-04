from functools import reduce
import logging
import math
import operator

from stuffbuf.writer.Source import Source
from stuffbuf.writer.fsr.parse import parsers, TapParsingError


class FSRSession:

    def __init__(self, tap_mask, mod_mask, bytedepth, init, limit):
        self.tap_mask = tap_mask
        self.mod_mask = mod_mask
        self.bytedepth = bytedepth
        self.init = init
        self.limit = limit

    def done(self, prev, new):
        return any([
            new == self.init,
            new == prev,
        ])

    def run(self):
        reg = self.init
        for _ in range(self.limit):
            yield (reg & self.mod_mask).to_bytes(
                self.bytedepth, byteorder='big'
            )
            tapped_bits = map(int, bin(reg & self.tap_mask)[2:])
            new_reg = (
                (reg << 1) | reduce(
                    operator.xor,
                    tapped_bits
                )
            ) & self.mod_mask
            if self.done(reg, new_reg):
                break
            else:
                reg = new_reg


class FSR(Source):

    @classmethod
    def fmt(cls):
        return 'fsr'

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        return dict(
            taps=self.parse_taps(args_dict.get('taps', '16,15,13,14')),
            init=int(args_dict.get('init', '0xffff'), 16),
            limit=int(args_dict.get('limit', '88200'))
        )

    def parse_taps(self, s):
        for parser_t in parsers:
            parser = parser_t()
            try:
                taps = parser.parse(s)
            except TapParsingError:
                continue
            else:
                return sorted(taps, reverse=True)

    def generate(self, taps, init, limit):
        tap_mask = reduce(operator.or_, map(lambda b: 1 << (b - 1), taps))
        logging.info('taps: {} == 0x{:x}'.format(taps, tap_mask))

        bytedepth = int(math.ceil(taps[0] / 8))
        mod_mask = (1 << max(taps)) - 1

        session = FSRSession(tap_mask, mod_mask, bytedepth, init, limit)
        return session.run()
