import logging
import operator
from itertools import repeat

from sympy import Dummy, fps, sequence, Symbol, sympify, oo
from sympy.abc import w
from sympy.polys import polytools
from sympy.series.formal import FormalPowerSeries

from stuffbuf.parse.exceptions import ParsingError


class ZTransformParser:

    def parse(self, s, depth=16):
        e = sympify(s)
        if e.is_polynomial(w):
            poly = polytools.poly(e)
        else:
            series = fps(e)
            poly = polytools.poly(series.polynomial(depth))

        logging.info('z-transform in w = 1 / z: {}'.format(poly))
        if all(pred() for pred in (
            lambda: isinstance(poly, polytools.Poly),
            lambda: poly == poly.diff().integrate(),
            lambda: w in poly.free_symbols,
        )):
            coeffs = [int(c) for c in poly.coeffs()]
            return lambda memory: sum(map(operator.mul, coeffs, memory))
        else:
            raise ParsingError(
                '''' please use the symbol w = 1 / z and provide an expression which
has only negative Laurent coefficients, e.g. exp(w) - 1
(corresponding to a causal z-transform). '''
            )
