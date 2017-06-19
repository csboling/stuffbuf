import logging
import operator

from sympy import sympify, solve
from sympy.abc import w, z
from sympy.functions import Abs
from sympy.series.residues import residue

# from stuffbuf.parse.exceptions import ParsingError


class ZTransformParser:

    def parse(self, s, depth=16):
        poly = sympify(s).series(1 / z, 0, depth + 1).removeO()
        logging.info('Laurent series: {}'.format(poly))

        inv_poly = poly.subs(z, 1 / w)
        poles = solve(inv_poly, w)

        coeffs = [
            sum(
                int(residue(poly * z**(k - 1), z, pole))
                for pole in poles if Abs(pole) < 1
            )
            for k in range(depth, 0, -1)
        ]
        logging.info('recurrence coeffs: {}'.format(coeffs))

        return lambda memory: sum(map(operator.mul, coeffs, memory))
