import logging

from abc import ABCMeta, abstractmethod
from io import BytesIO

def all_subclasses(cls):
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__()
            for g in all_subclasses(s)
    ]


class Writer(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def fmt(cls):
        pass

    @abstractmethod
    def write(self, source, target, *args, **kwargs):
        pass

    def bind_args(self, *args):
        bound = self.write

        def write(source, target):
            bound(source, target, **self.parse_args(args))
        self.write = write

    def parse_args(self, args):
        ret = dict()
        for arg in args:
            car, *cdr = arg.split('=')
            if len(cdr):
                ret[car] = cdr[0]
            else:
                ret[car] = True
        return ret

    @classmethod
    def create(cls, fmt):
        from stuffbuf.writer.Id import IdWriter
        try:
            impl = next(k for k in all_subclasses(cls) if k.fmt() == fmt)
        except StopIteration:
            logging.warning(
                "didn't recognize format '{}', "
                "falling back to binary output".format(fmt)
            )
            impl = IdWriter
        return impl()

    def __or__(left, right):
        class ChainedWriter(Writer):

            @classmethod
            def fmt(cls):
                return '{} | {}'.format(left.fmt(), right.fmt())

            def write(self, source, target):
                buf = BytesIO()
                left.write(source, buf)
                logging.info('-> {}'.format(right.fmt()))
                buf.seek(0)
                right.write(buf, target)

        return ChainedWriter()
