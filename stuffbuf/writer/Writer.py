from abc import ABCMeta, abstractmethod


class Writer(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def fmt(cls):
        pass

    @abstractmethod
    def write(self, source, outf, *args, **kwargs):
        pass

    @classmethod
    def create(cls, fmt):
        try:
            impl = next(k for k in cls.__subclasses__() if k.fmt() == fmt)
        except StopIteration:
            impl = IdWriter
        return impl()
