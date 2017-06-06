from functools import reduce
import logging
import math
import operator

from sympy.abc import x
from sympy.polys import Poly
from sympy.polys.domains import GF

from stuffbuf.writer import Writer
from stuffbuf.writer.fsr.FSR import FSR, FSRSession
from stuffbuf.writer.fsr.parse import parsers, TapParsingError


class LFSRSession(FSRSession):

    def __init__(self, taps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(taps)
        self.tap_mask = reduce(operator.or_, map(lambda b: 1 << (b - 1), taps))
        logging.info('taps: {} == 0x{:x}'.format(taps, self.tap_mask))

        self.bytedepth = int(math.ceil(taps[0] / 8))
        self.mod_mask = (1 << max(taps)) - 1

    def done(self, prev, new):
        return False

    def step(self, reg):
        return ((reg << 1) | self.feedback(reg)) & self.mod_mask

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
        args_dict = Writer.parse_args(args)
        fsr_args = super().parse_args(args)
        taps = self.parse_taps(args_dict.get('taps', '15,14,13,12'))
        return dict(
            taps=taps,
            **fsr_args
        )

    def create_session(self, taps, init, limit):
        return LFSRSession(taps, init, limit)

    @classmethod
    def parse_taps(cls, s):
        for parser_t in parsers:
            parser = parser_t()
            try:
                taps = list(parser.parse(s))
            except TapParsingError:
                continue
            else:
                logging.info('feedback poly: {}'.format(
                    cls.feedback_poly(taps)
                ))
                return sorted(taps, reverse=True)
        raise TapParsingError('Failed to parse taps input.')

    @staticmethod
    def coeffs_to_taps(coeffs):
        taps = []
        poly_order = len(coeffs) - coeffs.index(1)
        for i, b in enumerate(coeffs):
            if b == 1:
                taps.append(poly_order - i)
        return taps

    @staticmethod
    def taps_to_coeffs(taps):
        order = max(taps)
        coeffs = [0] * (order + 1)
        for tap in taps:
            coeffs[-(tap + 1)] = 1
        return coeffs

    @classmethod
    def feedback_poly(cls, taps):
        coeffs = cls.taps_to_coeffs(taps)
        return Poly.from_list(
            coeffs, x, domain=GF(2)
        ) + Poly.from_list(
            [1], x, domain=GF(2)
        )
