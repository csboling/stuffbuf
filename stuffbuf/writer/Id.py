from stuffbuf.writer.Writer import Writer


class IdWriter(Writer):

    @classmethod
    def fmt(cls):
        return 'id'

    def write(self, source, target):
        target.write(source.read())
