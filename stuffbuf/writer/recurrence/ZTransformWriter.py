from stuffbuf.parse.ztransform import ZTransformParser
from stuffbuf.writer.recurrence.RecurrenceWriter import RecurrenceWriter


class ZTransformWriter(RecurrenceWriter):

    @classmethod
    def fmt(cls):
        return 'zx'

    def parser(self):
        return ZTransformParser()
