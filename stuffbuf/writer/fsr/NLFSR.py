import ast
import logging
import math

from stuffbuf.writer import Writer
from stuffbuf.writer.fsr.FSR import FSR, FSRSession
from stuffbuf.writer.fsr.exceptions import UnknownFeedbackOperator


class NLFSRSession(FSRSession):

    def __init__(self, thunk, order, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thunk = thunk
        self.bytedepth = int(math.ceil(order / 8))
        self.mod_mask = (1 << (self.bytedepth * 8)) - 1

    def feedback(self, reg):
        bits = list(map(int, bin(reg)[2:].zfill(self.bytedepth * 8)))
        return self.thunk(bits)


class NLFSR(FSR):

    @classmethod
    def fmt(cls):
        return 'nlfsr'

    def parse_args(self, args):
        args_dict = Writer.parse_args(self, args)
        fsr_args = super().parse_args(args)
        return dict(
            feedback=self.parse_feedback(
                args_dict.get('feedback', '16 ^ 15 ^ 13 ^ 14')
            ),
            **fsr_args
        )

    def parse_feedback(self, s):
        logging.info('feedback formula: {}'.format(s))
        exp = ast.parse(s, mode='eval')
        self.order = 0
        return self.eval(exp.body)

    def eval(self, exp):
        if isinstance(exp, ast.Num):
            self.order = max(self.order, exp.n)
            return lambda bits: self.get_bit(bits, exp.n)
        elif isinstance(exp, ast.UnaryOp):
            op = self.get_op(exp.op)
            operand = self.eval(exp.operand)
            return lambda bits: op(operand(bits))
        elif isinstance(exp, ast.BinOp):
            op = self.get_op(exp.op)
            left = self.eval(exp.left)
            right = self.eval(exp.right)
            return lambda bits: op(left(bits), right(bits))

    def get_bit(self, bits, exponent):
        return bits[-(exponent - 1)]

    def get_op(self, op):
        if isinstance(op, ast.Invert):
            return lambda b: 1 - b
        elif isinstance(op, ast.BitOr):
            return lambda l, r: l | r
        elif isinstance(op, (ast.BitAnd, ast.Mult)):
            return lambda l, r: l & r
        elif isinstance(op, (ast.BitXor, ast.Add, ast.Sub)):
            return lambda l, r: l ^ r
        else:
            raise UnknownFeedbackOperator

    def create_session(self, feedback, *args, **kwargs):
        return NLFSRSession(feedback, order=self.order, *args, **kwargs)
