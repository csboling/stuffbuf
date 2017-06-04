from stuffbuf.writer.fsr.parse.TapParser import TapParser
from stuffbuf.writer.fsr.parse.exceptions import TapParsingError


class ListParser(TapParser):

    def parse(self, s):
        taps = s.split(',')
        if taps[0] == s:
            raise TapParsingError
        else:
            return map(int, taps)
