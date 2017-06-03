from functools import reduce
import operator

from stuffbuf.writer.Source import Source


class LFSR(Source):
    @classmethod
    def fmt(cls):
        return 'lfsr'

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        return dict(
            taps=sorted(
                map(
                    int,
                    args_dict.get('taps', '16,15,13,14').split(',')
                ),
                reverse=True
            ),
            init=int(args_dict.get('init', '0xffff'), 16)
        )

    def generate(self, taps, init):
        tap_mask = reduce(operator.or_, map(lambda b: 1 << (b - 1), taps))
        bytedepth = taps[0] // 8
        print('taps:', taps, '== 0x{:x}'.format(tap_mask))
        mod_mask = (1 << max(taps)) - 1

        reg = init & mod_mask
        while True:
            yield (reg & mod_mask).to_bytes(bytedepth, byteorder='big')
            set_bits = map(int, bin(reg & tap_mask)[2:])
            reg = ((reg << 1) | reduce(operator.xor, set_bits)) & mod_mask
            if reg == init:
                break
