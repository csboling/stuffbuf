from abc import ABCMeta, abstractmethod

from stuffbuf.writer.Source import Source


class FSRSession(metaclass=ABCMeta):

    def __init__(self, init, limit):
        self.init = init
        self.limit = limit

    def done(self, prev, new):
        return any([
            new == self.init,
            new == prev,
        ])

    @abstractmethod
    def feedback(self, reg):
        pass

    def step(self, reg):
        return ((reg << 1) | self.feedback(reg)) & self.mod_mask

    def run(self):
        reg = self.init
        for _ in range(self.limit):
            yield (reg & self.mod_mask).to_bytes(
                self.bytedepth, byteorder='big'
            )
            new_reg = self.step(reg)
            if self.done(reg, new_reg):
                break
            else:
                reg = new_reg


class InvertibleFSRSession(FSRSession):

    @abstractmethod
    def inverse(self, reg):
        pass

    def unstep(self, reg):
        return (
            (reg >> 1) |
            (self.inverse(reg) << 8 * self.bytedepth)
        ) & self.mod_mask


class FSR(Source):

    def parse_args(self, args):
        args_dict = super().parse_args(args)
        return dict(
            init=int(args_dict.get('init', '0xffff'), 16),
            limit=int(args_dict.get('limit', '88200'))
        )

    @abstractmethod
    def create_session(self, *args, **kwargs):
        pass

    def generate(self, *args, **kwargs):
        session = self.create_session(*args, **kwargs)
        return session.run()
