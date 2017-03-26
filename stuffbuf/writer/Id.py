from stuffbuf.writer.Writer import Writer


class IdWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'id'

    def write(self, source, outf):
        with open(outf, 'wb') as f:
            f.write(source.read())
