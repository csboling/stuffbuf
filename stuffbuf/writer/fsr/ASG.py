from collections import namedtuple
import logging
import math

from stuffbuf.writer.Writer import Writer
from stuffbuf.writer.fsr.FSR import FSR, FSRSession
from stuffbuf.writer.fsr.LFSR import LFSR, LFSRSession


class ASGSession(FSRSession):

    RegCtx = namedtuple('RegCtx', ['reg', 'state'])

    def __init__(self, specs, init, *args, **kwargs):
        super().__init__(init=0, *args, **kwargs)
        max_tap = max(max(taps) for taps, _ in specs)
        self.bytedepth = int(math.ceil(max_tap / 8))
        self.mod_mask = (1 << max_tap) - 1
        self.regs = [
            LFSRSession(taps=taps, init=init, *args, **kwargs)
            for taps, init in specs
        ]
        n = 2**(len(specs) - 1)
        m = 1
        while n >= m:
            m += 1
            n /= 2
        self.dom_reg_count = math.floor(n)
        self.max_reg_mask = 2**(len(self.regs) - self.dom_reg_count) - 1
        self.reg_ctxs = [self.RegCtx(reg, reg.run()) for reg in self.regs]
        self.dom_regs = self.reg_ctxs[: self.dom_reg_count]
        self.sub_regs = self.reg_ctxs[self.dom_reg_count:]

        logging.info('{} dominant regs'.format(self.dom_reg_count))

    def get_state(self, ctx):
        state = next(ctx.state)
        return int.from_bytes(state, byteorder='big')

    def step(self, reg):
        control_state = [self.get_state(ctx) for ctx in self.dom_regs]
        # print(control_state)
        control_bits = [
            ctx.reg.feedback(control_state[i])
            for i, ctx in enumerate(self.dom_regs)
        ]
        target_index = int(''.join(map(str, control_bits)), 2)
        target = self.sub_regs[target_index & self.max_reg_mask]
        target_state = self.get_state(target)
        target_out = target.reg.feedback(target_state)
        return target_state ^ control_state[0]


class ASG(FSR):

    @classmethod
    def fmt(cls):
        return 'asg'

    def parse_args(self, args):
        args_dict = Writer.parse_args(args)
        specs = list(zip(
            (
                LFSR.parse_taps(taps)
                for taps in args_dict.get(
                    'taps',
                    'x**16 + x**15 + x**14 + x**13 + 1,'
                    'x**15 + x**14 + 1,'
                    'x**14 + x**13 + x**3 + x**2 + 1'
                ).split(',')
            ),
            (
                int(init, 16)
                for init in args_dict.get(
                    'init',
                    '0x2492,0x4210,0x8102'
                ).split(',')
            ),
        ))
        limit = int(args_dict.get('limit', '88200'))
        return dict(specs=specs, limit=limit, init=0)

    def create_session(self, specs, *args, **kwargs):
        return ASGSession(specs, *args, **kwargs)
