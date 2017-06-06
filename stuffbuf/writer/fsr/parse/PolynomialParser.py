import logging

from sympy.polys.polytools import poly_from_expr, trunc

from stuffbuf.writer.fsr.parse.TapParser import TapParser
from stuffbuf.writer.fsr.parse.exceptions import TapParsingError


class PolynomialParser(TapParser):

    def parse(self, s):
        try:
            poly, meta = poly_from_expr(s)
        except SyntaxError:
            raise TapParsingError
        else:
            gf = trunc(poly, 2)
            self.screen_polys(gf, meta)
            logging.info('input poly [ℤ]: {}'.format(poly))
            return self.coeffs_to_taps(gf.all_coeffs()[:-1])

    @staticmethod
    def screen_polys(poly, meta):
        if len(meta['gens']) > 1:
            raise TapParsingError
        if poly.all_coeffs()[-1] != 1:
            raise TapParsingError('Zero coefficient must be 1.')
