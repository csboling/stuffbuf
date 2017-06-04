from functools import reduce
import logging
import math
import operator

from stuffbuf.writer.Source import Source


class LFSR(Source):
    @classmethod
    def fmt(cls):
        return 'lfsr'

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        return dict(
            taps=self.parse_taps(args_dict.get('taps', '16,15,13,14')),
            init=int(args_dict.get('init', '0xffff'), 16)
        )

    def parse_taps(self, s):
        try:
            taps_int = int(s, 16)
        except ValueError:
            raw_taps = map(int, s.split(','))
        else:
            raw_taps = []
            bin_taps = bin(taps_int)[2:]
            poly_order = len(bin_taps) - bin_taps.index('1')
            for i, b in enumerate(bin_taps):
                if b == '1':
                    raw_taps.append(poly_order - i)
        return sorted(raw_taps, reverse=True)


    def generate(self, taps, init):
        tap_mask = reduce(operator.or_, map(lambda b: 1 << (b - 1), taps))
        logging.info('taps: {} == 0x{:x}'.format(taps, tap_mask))

        bytedepth = int(math.ceil(taps[0] / 8))
        mod_mask = (1 << max(taps)) - 1

        reg = init
        while True:
            yield (reg & mod_mask).to_bytes(bytedepth, byteorder='big')
            set_bits = map(int, bin(reg & tap_mask)[2:])
            new_reg = ((reg << 1) | reduce(operator.xor, set_bits)) & mod_mask
            if new_reg == init or new_reg == reg:
                break
            else:
                reg = new_reg
