from abc import ABCMeta, abstractmethod
from io import BytesIO


class Writer(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def fmt(cls):
        pass

    def write(self, source, target, *args, **kwargs):
        pass

    def bind_args(self, *args):
        bound = self.write

        def write(source, target):
            bound(source, target, *args)
        self.write = write

    @classmethod
    def create(cls, fmt):
        from stuffbuf.writer.Id import IdWriter
        try:
            impl = next(k for k in cls.__subclasses__() if k.fmt() == fmt)
        except StopIteration:
            print(
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
                print('-> {}'.format(right.fmt()))
                buf.seek(0)
                right.write(buf, target)

        return ChainedWriter()
