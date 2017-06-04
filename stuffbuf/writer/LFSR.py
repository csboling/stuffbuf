from abc import ABCMeta, abstractmethod
from functools import reduce
import logging
import math
import operator
from typing import Iterable

from sympy.polys.polytools import poly_from_expr
from sympy.polys.galoistools import gf_from_int_poly


class TapParsingError(Exception):
    pass


class TapParser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self, s) -> Iterable[int]:
        pass

    @staticmethod
    def coeffs_to_taps(coeffs):
        taps = []
        poly_order = len(coeffs) - coeffs.index(1)
        for i, b in enumerate(coeffs):
            if b == 1:
                taps.append(poly_order - i)
        return taps


class IntParser(TapParser):

    def parse(self, s):
        try:
            taps_int = int(s, 16)
        except ValueError:
            raise TapParsingError
        else:
            bin_taps = bin(taps_int)[2:]
            return self.coeffs_to_taps(map(int, bin_taps))


class ListParser(TapParser):

    def parse(self, s):
        taps = s.split(',')
        if taps[0] == s:
            raise TapParsingError
        else:
            return map(int, taps)


class PolynomialParser(TapParser):

    def parse(self, s):
        try:
            poly, meta = poly_from_expr(s)
        except SyntaxError:
            raise TapParsingError
        else:
            self.screen_polys(poly, meta)
            gf_poly = gf_from_int_poly(poly.coeffs(), 2)
            return self.coeffs_to_taps(gf_poly)

    @staticmethod
    def screen_polys(poly, meta):
        if len(meta['gens']) > 1:
            raise TapParsingError


class LFSRSession:

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
            yield (reg & self.mod_mask).to_bytes(self.bytedepth, byteorder='big')
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


class LFSR(Source):

    @classmethod
    def fmt(cls):
        return 'lfsr'

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        return dict(
            taps=self.parse_taps(args_dict.get('taps', '16,15,13,14')),
            init=int(args_dict.get('init', '0xffff'), 16),
            limit=int(args_dict.get('limit', '88200'))
        )

    @property
    def parsers(self):
        return [
            IntParser,
            ListParser,
            PolynomialParser,
        ]

    def parse_taps(self, s):
        for parser_t in self.parsers:
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

        session = LFSRSession(tap_mask, mod_mask, bytedepth, init, limit)
        return session.run()
