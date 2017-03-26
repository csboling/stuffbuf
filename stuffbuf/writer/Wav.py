import wave

from stuffbuf.writer.Writer import Writer


class WavWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'wav'

    def write(self, source, outf):
        w = wave.open(outf, mode='wb')
        w.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
        w.writeframes(source.read())
