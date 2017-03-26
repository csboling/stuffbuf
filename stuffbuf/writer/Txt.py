from stuffbuf.writer.Writer import Writer


class TxtWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'txt'

    def write(self, source, out, encoding='utf-8'):
        with open(out, 'w') as f:
            f.write(source.read().decode(encoding))
