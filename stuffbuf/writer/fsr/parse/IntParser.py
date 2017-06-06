from stuffbuf.writer.fsr.parse.TapParser import TapParser
from stuffbuf.writer.fsr.parse.exceptions import TapParsingError


class IntParser(TapParser):

    def parse(self, s):
        try:
            taps_int = int(s, 16)
        except ValueError:
            raise TapParsingError
        else:
            bin_taps = bin(taps_int)[2:]
            return self.coeffs_to_taps(list(map(int, bin_taps)))
