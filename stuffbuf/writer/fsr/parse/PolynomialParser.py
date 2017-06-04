import logging

from sympy.polys.polytools import poly_from_expr
from sympy.polys.galoistools import gf_from_int_poly

from stuffbuf.writer.fsr.parse.TapParser import TapParser
from stuffbuf.writer.fsr.parse.exceptions import TapParsingError


class PolynomialParser(TapParser):

    def parse(self, s):
        try:
            poly, meta = poly_from_expr(s)
        except SyntaxError:
            raise TapParsingError
        else:
            self.screen_polys(poly, meta)
            gf_poly = gf_from_int_poly(poly.coeffs(), 2)
            logging.info('GF(2) coefficients: {}'.format(gf_poly))
            return self.coeffs_to_taps(gf_poly)

    @staticmethod
    def screen_polys(poly, meta):
        if len(meta['gens']) > 1:
            raise TapParsingError
