import wave

from stuffbuf.writer.Writer import Writer


class WavWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'wav'

    def write(self, source, target):
        w = wave.open(target, mode='wb')
        w.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
        w.writeframes(source.read())
