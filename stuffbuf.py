# usage:
# head -c 44100 /dev/urandom | python3 stuffbuf.py png output.png [color]
# heac -c 44100 /dev/urandom | python3 stuffbuf.py wav output.wav

from abc import ABCMeta, abstractmethod
from io import BytesIO
from sys import stdin, argv
import wave

from PIL import Image


class Writer(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def fmt(cls):
        pass

    @abstractmethod
    def write(self, outf, *args, **kwargs):
        pass

    @classmethod
    def create(cls, fmt):
        try:
            impl = next(k for k in cls.__subclasses__() if k.fmt() == fmt)
        except StopIteration:
            impl = IdWriter
        return impl()


class IdWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'id'

    def write(self, outf):
        with open(outf, 'wb') as f:
            f.write(stdin.buffer.read())


class PngWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'png'

    @staticmethod
    def get_dims(n):
        w = n
        h = 1
        while w > h + 1:
            w //= 2
            h *= 2
            return (w, h)

    def write(self, outf, color=False):
        buf = stdin.buffer.read()
        print()

        count = len(buf)
        print('{} bytes'.format(count))

        if color:
            count //= 3
            mode = 'RGB'
        else:
            mode = 'L'

            w, h = self.get_dims(count)
            print('{} by {}'.format(w, h))
            bytecount = w * h * (3 if color else 1)
            buf = buf[:bytecount]
            print('{} byte bitmap'.format(len(buf)))

            im = Image.frombuffer(mode, (w, h), buf, 'raw', mode, 0, 1)
            im.save(outf, 'PNG')


class WavWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'wav'

    def write(self, outf):
        w = wave.open(outf, mode='wb')
        w.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
        w.writeframes(stdin.buffer.read())


if __name__ == '__main__':
    w = Writer.create(argv[1])
    w.write(*argv[2:])
