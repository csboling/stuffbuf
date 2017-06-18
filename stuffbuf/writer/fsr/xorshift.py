from stuffbuf.writer import Writer
from stuffbuf.writer.fsr.LFSR import LFSR, LFSRSession
from stuffbuf.writer.fsr.parse import parsers, TapParsingError


class XorshiftSession(LFSRSession):

    def __init__(self, multiplicand, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.multiplicand = multiplicand

    @staticmethod
    def shift(reg, shift):
        if shift > 0:
            return reg << shift
        else:
            return reg >> -shift

    def step(self, reg):
        return self.feedback(reg) & self.mod_mask

    def feedback(self, reg):
        for shift in self.taps:
            reg ^= self.shift(reg, shift)
        if self.multiplicand:
            reg *= self.multiplicand
        return reg


class Xorshift(LFSR):

    @classmethod
    def fmt(cls):
        return 'xorshift'

    def create_session(self, multiplicand, taps, init, limit):
        return XorshiftSession(multiplicand, taps, init, limit)

    def parse_args(self, args):
        args_dict = Writer.parse_args(args)
        lfsr_args = super().parse_args(args)

        multiplicand = None
        try:
            multiplicand = int(args_dict.get('multiplicand', '0x1234'), 16)
        except ValueError:
            pass

        return dict(
            multiplicand=multiplicand,
            **lfsr_args
        )

    @classmethod
    def parse_taps(cls, s):
        for parser_t in parsers:
            parser = parser_t()
            try:
                taps = list(parser.parse(s))
            except TapParsingError:
                continue
            else:
                return taps
        raise TapParsingError('Failed to parse taps input.')
