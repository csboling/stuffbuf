from abc import ABCMeta, abstractmethod

from stuffbuf.writer import Writer


class Source(Writer):
    @classmethod
    @abstractmethod
    def fmt(cls):
        pass

    @abstractmethod
    def generate(self, *args, **kwargs):
        pass

    def write(self, source, target, *args, **kwargs):
        for b in self.generate(*args, **kwargs):
            target.write(b)
