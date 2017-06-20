import logging
import operator

from sympy import sympify, oo
from sympy.abc import z
from sympy.functions import re


class ZTransformParser:

    def parse(self, s, depth=16):
        e = sympify(s)
        s = e.series(z, oo, depth + 1)
        logging.info(s)
        coeffs = [float(re(s.coeff(z, n))) for n in range(-depth, 1)]
        logging.info('coeffs: {}'.format(coeffs))
        return lambda memory: sum(map(operator.mul, coeffs, list(memory) + [1]))
