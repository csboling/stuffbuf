from functools import reduce
import logging
import math
import operator

from stuffbuf.writer import Writer
from stuffbuf.writer.fsr.FSR import FSR, FSRSession
from stuffbuf.writer.fsr.parse import parsers, TapParsingError


class LFSRSession(FSRSession):

    def __init__(self, taps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tap_mask = reduce(operator.or_, map(lambda b: 1 << (b - 1), taps))
        logging.info('taps: {} == 0x{:x}'.format(taps, self.tap_mask))

        self.bytedepth = int(math.ceil(taps[0] / 8))
        self.mod_mask = (1 << max(taps)) - 1

    def feedback(self, reg):
        tapped_bits = map(int, bin(reg & self.tap_mask)[2:])
        return reduce(
            operator.xor,
            tapped_bits
        )


class LFSR(FSR):

    @classmethod
    def fmt(cls):
        return 'lfsr'

    def parse_args(self, args):
        args_dict = Writer.parse_args(self, args)
        fsr_args = super().parse_args(args)
        taps = self.parse_taps(args_dict.get('taps', '16,15,13,14'))
        return dict(
            taps=taps,
            **fsr_args
        )

    def create_session(self, taps, init, limit):
        return LFSRSession(taps, init, limit)

    def parse_taps(self, s):
        for parser_t in parsers:
            parser = parser_t()
            try:
                taps = parser.parse(s)
            except TapParsingError:
                continue
            else:
                return sorted(taps, reverse=True)
