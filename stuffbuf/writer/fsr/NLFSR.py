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
        args_dict = Writer.parse_args(args)
        fsr_args = super().parse_args(args)
        return dict(
            feedback=self.parse_feedback(
                args_dict.get('feedback', '16 ^ 15 ^ 13 ^ 14')
            ),
            **fsr_args
        )

    @classmethod
    def parse_feedback(self, s):
        logging.info('feedback formula: {}'.format(s))
        exp = ast.parse(s, mode='eval')
        self.order = 0
        return self.eval(exp.body)

    @classmethod
    def eval(cls, exp):
        if isinstance(exp, ast.Num):
            cls.order = max(cls.order, exp.n)
            return lambda bits: cls.get_bit(bits, exp.n)
        elif isinstance(exp, ast.UnaryOp):
            op = cls.get_op(exp.op)
            operand = cls.eval(exp.operand)
            return lambda bits: op(operand(bits))
        elif isinstance(exp, ast.BinOp):
            op = cls.get_op(exp.op)
            left = cls.eval(exp.left)
            right = cls.eval(exp.right)
            return lambda bits: op(left(bits), right(bits))

    @classmethod
    def get_bit(cls, bits, exponent):
        return bits[-(exponent - 1)]

    @classmethod
    def get_op(cls, op):
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
