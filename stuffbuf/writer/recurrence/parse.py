import ast
from collections import deque


class RecurrenceRelation:
    def __init__(self, feedback, depth):
        self.feedback = feedback
        self.depth = depth

    def run(self, init, limit):
        reg = init
        memory = deque([], self.depth)
        for _ in range(limit):
            yield reg
            memory.append(reg)
            reg = self.feedback(reg, memory)


# 'z**-1 * x + z**-2 * x' == 'z**-1 * x * (1 + z**-1)'

class RecurrenceRelationParsingError(Exception):
    pass


class DelayElement:
    def __init__(self, delay):
        self.delay = delay

    def __mul__(self, operand):



class RecurrenceRelationParser:
    def parse(self, s):
        return self.eval(ast.parse(s, mode='eval'))

    def eval(self, e):
        if all(f() for f in [
            lambda: isinstance(e, ast.BinOp),
            lambda: e.op == ast.Pow isinstance(e.left, ast.Name),
            lambda: e.left.id == 'z',
        ]):
            return DelayElement(self.eval(e.right))
        # elif isinstance(e, ast.Subscript):
        #     return BitSlice(self.eval(e.value), e.slice)
