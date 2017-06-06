from collections import namedtuple
from functools import reduce
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
        logging.info('{} regs total'.format(len(self.regs)))
        m = 0
        while 2**m < (len(specs) - m):
            m += 1
        self.dom_reg_count = m
        self.sub_reg_count = len(self.regs) - m
        self.reg_ctxs = [self.RegCtx(reg, reg.run()) for reg in self.regs]
        self.dom_regs = self.reg_ctxs[: self.dom_reg_count]
        self.sub_regs = self.reg_ctxs[self.dom_reg_count - 1:]

        logging.info('{} dominant regs'.format(self.dom_reg_count))

    def get_state(self, ctx):
        state = next(ctx.state)
        return int.from_bytes(state, byteorder='big')

    def step(self, reg):
        control_state = [self.get_state(ctx) for ctx in self.dom_regs]
        control_bits = [
            ctx.reg.feedback(control_state[i])
            for i, ctx in enumerate(self.dom_regs)
        ]
        target_index = int(''.join(map(str, control_bits)), 2)
        target = self.sub_regs[target_index % self.sub_reg_count]
        target_state = self.get_state(target)
        target_out = target.reg.feedback(target_state)
        return self.feedback(target_state, control_state, control_bits)

    def feedback(self, target, controls, control_bits):
        # print(control_bits)
        return target ^ reduce(
            lambda x, y: x & ~y,
            (control for (control, bit) in zip(controls, control_bits) if bit),
            1
        )


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
                    ','.join([
                        'x**16 + x**13 + x**10 + x**7 + x**4 + x + 1',
                        'x**15 + x**12 + x**9  + x**6 + x + 1',
                        'x**14 + x**11 + x**8  + x**5 + 1',
                        'x**4 + x**2 + 1',
                        'x**5 + x**3 + 1',
                        'x**5 + x**3 + 1',
                        'x**5 + x**3 + 1',
                    ])
                ).split(',')
            ),
            (
                int(init, 16)
                for init in args_dict.get(
                    'init',
                    '0x2492,0x4210,0x8102,0xdead,0xbeef,0xcafe,0xc0de'
                ).split(',')
            ),
        ))
        print(specs)
        limit = int(args_dict.get('limit', '88200'))
        return dict(specs=specs, limit=limit, init=0)

    def create_session(self, specs, *args, **kwargs):
        return ASGSession(specs, *args, **kwargs)
