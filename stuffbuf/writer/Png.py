import logging

from PIL import Image

from stuffbuf.writer.Writer import Writer


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

    def write(self, source, target, color=False):
        buf = source.read()
        count = len(buf)
        logging.info('{} bytes'.format(count))

        if color:
            count //= 3
            mode = 'RGB'
        else:
            mode = 'L'

        w, h = self.get_dims(count)
        logging.info('{} by {}'.format(w, h))
        bytecount = w * h * (3 if color else 1)
        buf = buf[:bytecount]
        logging.info('{} byte bitmap'.format(len(buf)))

        im = Image.frombuffer(mode, (w, h), buf, 'raw', mode, 0, 1)
        im.save(target, 'PNG')
