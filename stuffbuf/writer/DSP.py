import logging

import numpy as np
from scipy.signal import convolve

from stuffbuf.writer.Writer import Writer


class ConvolveWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'convolve'

    @staticmethod
    def convolve(kernel, signal):
        x = np.array(list(signal))
        h = np.array(list(kernel))
        y = convolve(x, h)
        return bytes(map(int, 255 * y / max(y)))

    def write(self, source, target, kernel_f):
        logging.info('open: {}'.format(kernel_f))
        with open(kernel_f, 'rb') as kernel:
            target.write(self.convolve(kernel.read(), source.read()))
