import logging

from sympy import Function, sympify, pi, sin
from sympy.abc import n, x
from sympy.utilities.lambdify import lambdify, implemented_function


class RecurrenceRunner:

    def __init__(self, exp, memdepth):
        self.time = 0

        def x_impl_fn(n):
            return self.memory[-(n % memdepth)]

        x_impl = implemented_function(
            Function('x'),
            x_impl_fn
        )
        self.exp = exp.subs(x, x_impl)

    def __call__(self, memory):
        self.memory = memory
        e = self.exp.subs(n, self.time)
        lam_x = lambdify((), e)
        self.time += 1
        return lam_x()


class RecurrenceParser:

    def parse(self, s, depth, **kwargs):
        return RecurrenceRunner(sympify(s), depth)
