from abc import ABCMeta, abstractmethod
from typing import Iterable


class TapParser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self, s) -> Iterable[int]:
        pass

    @staticmethod
    def coeffs_to_taps(coeffs):
        taps = []
        poly_order = len(coeffs) - coeffs.index(1)
        for i, b in enumerate(coeffs):
            if b == 1:
                taps.append(poly_order - i)
        return taps
